# backend/filesharehub_v2/tasks/generate_thumbnail.py
import os
import logging
import time
from celery import shared_task
from PIL import Image, UnidentifiedImageError
from django.conf import settings
from filesharehub_v2.models.filerecord import FileRecord
from filesharehub_v2.utils.cache import cache_thumbnail_path
from urllib.parse import unquote
from django.core.cache import cache
from django.db import transaction

logger = logging.getLogger("filesharehub_v2")

@shared_task(bind=True, max_retries=4)
def generate_thumbnail(self, file_id):
    """
    Verilen file_id için thumbnail oluşturur ve kaydeder.
    """
    start_time = time.time()
    lock_key = f"thumb-lock:{file_id}"
    if not cache.add(lock_key, "1", timeout=60):
        return

    try:
        file = FileRecord.objects.select_related().get(file_id=file_id)
        abs_path = os.path.join(settings.NETWORK_FOLDER_PATH, unquote(file.full_path))

        # Dosya erişim ve tür kontrolü
        if not os.path.isfile(abs_path):
            logger.error(f"[ThumbnailError] Dosya bulunamadı: {abs_path}")
            with transaction.atomic():
                file.thumbnail_path = None
                file.save(update_fields=["thumbnail_path"])
            return

        if not file.is_image:
            
            with transaction.atomic():
                file.thumbnail_path = None
                file.save(update_fields=["thumbnail_path"])
            return

        # Thumbnail dosya yolları
        thumb_name = f"{file_id}.jpg"
        rel_thumb_path = os.path.join("thumbs", thumb_name)
        abs_thumb_path = os.path.join(settings.MEDIA_ROOT, rel_thumb_path)
        os.makedirs(os.path.dirname(abs_thumb_path), exist_ok=True)

        # Thumbnail oluşturma
        try:
            with Image.open(abs_path) as img:
                img.verify()  # Dosyanın geçerli bir görsel olduğunu kontrol et
                img = Image.open(abs_path)  # Yeniden aç (verify sonrası dosya kapanır)
                img.thumbnail((128, 128))  # Daha küçük boyut, performans için
                img.convert("RGB").save(
                    abs_thumb_path,
                    "JPEG",
                    quality=75,
                    optimize=True,
                    progressive=True
                )
        except UnidentifiedImageError:
            logger.warning(f"[ThumbnailSkip] Geçersiz görsel formatı: {abs_path}")
            with transaction.atomic():
                file.thumbnail_path = None
                file.save(update_fields=["thumbnail_path"])
            return
        except Exception as e:
            logger.error(f"[ThumbnailError] Thumbnail oluşturulurken hata: {abs_path} - {str(e)}")
            raise self.retry(exc=e, countdown=30)  # Daha kısa retry süresi

        # Thumbnail path'i kaydet
        with transaction.atomic():
            file.thumbnail_path = rel_thumb_path
            file.save(update_fields=["thumbnail_path"])
        cache_thumbnail_path(abs_path, abs_thumb_path)



    except FileRecord.DoesNotExist:
        logger.warning(f"[ThumbnailSkip] file_id={file_id} → DB kaydı yok")
    except Exception as e:
        logger.error(f"[ThumbnailFatal] file_id={file_id} → {str(e)}")
        raise self.retry(exc=e, countdown=30)
    finally:
        cache.delete(lock_key)

@shared_task
def scan_directory_task(abs_path):
    """
    Verilen dizini tarar ve dosyaları senkronize eder.
    """
    from filesharehub_v2.utils.fs_scanner import sync_directory
    try:
        
        sync_directory(abs_path)
        
    except Exception as e:
        logger.error(f"[DirectoryScanError] {abs_path} → {str(e)}")
        raise  # Hata fırlatarak Celery'nin retry mekanizmasını tetikle
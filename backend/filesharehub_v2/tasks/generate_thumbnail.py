# backend/filesharehub_v2/tasks/generate_thumbnail.py
import os
import time
from celery import shared_task
from PIL import Image, UnidentifiedImageError
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from urllib.parse import unquote

from filesharehub_v2.models.filerecord import FileRecord
from filesharehub_v2.utils.cache import cache_thumbnail_path

@shared_task(bind=True, max_retries=4)
def generate_thumbnail(self, file_id):
    """
    Verilen file_id için thumbnail oluşturur ve kaydeder.
    Bu sürümde loglama tamamen kaldırılmıştır. Hatalar konsola yazdırılır.
    """
    lock_key = f"thumb-lock:{file_id}"
    if not cache.add(lock_key, "1", timeout=120): # Kilit süresini 2dk yapalım
        return

    try:
        file = FileRecord.objects.get(file_id=file_id)
        abs_path = os.path.join(settings.NETWORK_FOLDER_PATH, unquote(file.full_path))

        # Dosya erişim ve tür kontrolü
        if not os.path.isfile(abs_path):
            # Dosya yoksa thumbnail yolunu temizle ve sessizce bitir.
            with transaction.atomic():
                if file.thumbnail_path is not None:
                    file.thumbnail_path = None
                    file.save(update_fields=["thumbnail_path"])
            return

        if not file.is_image:
            # Görsel değilse thumbnail yolunu temizle ve sessizce bitir.
            with transaction.atomic():
                if file.thumbnail_path is not None:
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
                img.verify()
                # verify() sonrası dosyayı yeniden açmak gerekir
                with Image.open(abs_path) as img_reopened:
                    img_reopened.thumbnail((128, 128))
                    img_reopened.convert("RGB").save(
                        abs_thumb_path, "JPEG",
                        quality=80, optimize=True, progressive=True
                    )
        except UnidentifiedImageError:
            # Geçersiz görsel formatı ise thumbnail yolunu temizle ve sessizce bitir.
            with transaction.atomic():
                if file.thumbnail_path is not None:
                    file.thumbnail_path = None
                    file.save(update_fields=["thumbnail_path"])
            return
        except Exception as e:
            print(f"[Thumbnail-Task-Error] file_id={file_id}, path={abs_path} - Hata: {e}")
            raise self.retry(exc=e, countdown=60)

        # Thumbnail path'i kaydet
        with transaction.atomic():
            file.thumbnail_path = rel_thumb_path
            file.save(update_fields=["thumbnail_path"])
        
        cache_thumbnail_path(abs_path, abs_thumb_path)

    except FileRecord.DoesNotExist:
        # DB kaydı yoksa sessizce bitir.
        pass
    except Exception as e:
        print(f"[Thumbnail-Task-Fatal-Error] file_id={file_id} - Hata: {e}")
        raise self.retry(exc=e, countdown=60)
    finally:
        cache.delete(lock_key)


@shared_task(bind=True, max_retries=3)
def scan_directory_task(self, abs_path):
    """
    Verilen dizini tarar ve dosyaları senkronize eder. Loglama yapmaz.
    """
    from filesharehub_v2.utils.fs_scanner import sync_directory
    try:
        sync_directory(abs_path)
    except Exception as e:
        print(f"[DirectoryScan-Task-Error] Path: {abs_path} - Hata: {e}")
        raise self.retry(exc=e, countdown=120)
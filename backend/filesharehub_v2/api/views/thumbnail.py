# backend/filesharehub_v2/api/views/thumbnail.py

import os
import sys
import time
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from celery.result import AsyncResult

from filesharehub_v2.api.permissions import ReadOnlyPermission
from filesharehub_v2.models.filerecord import FileRecord
from filesharehub_v2.tasks.generate_thumbnail import generate_thumbnail
from filesharehub_v2.utils.cache import get_cached_thumbnail
from filesharehub_v2.utils.rules import is_safe_path


class ThumbnailView(APIView):
    """
    Bu sürüm, log dosyasına HİÇBİR kayıt atmayacak şekilde düzenlenmiştir.
    Sadece çok kritik hatalar, log dosyası yerine konsola yazdırılır.
    """
    permission_classes = [IsAuthenticated, ReadOnlyPermission]

    def get(self, request, file_id):
        try:
            file = FileRecord.objects.get(file_id=file_id)
        except FileRecord.DoesNotExist:
            raise Http404("Dosya bulunamadı.")

        if not file.is_image:
            raise Http404("İstenen dosya bir görsel değil.")

        abs_path = os.path.join(settings.NETWORK_FOLDER_PATH, file.full_path)
        try:
            is_safe_path(settings.NETWORK_FOLDER_PATH, abs_path)
        except PermissionDenied as e:
            # Kritik güvenlik hatasını log dosyası yerine konsola yazdır
            print(f"GÜVENLİK UYARISI: {e}", file=sys.stderr)
            raise Http404("Geçersiz dosya yolu.")

        # Hızlı yollar (DB ve Cache)
        if file.thumbnail_path and os.path.exists(os.path.join(settings.MEDIA_ROOT, file.thumbnail_path)):
            return FileResponse(open(os.path.join(settings.MEDIA_ROOT, file.thumbnail_path), "rb"), content_type="image/jpeg", headers={"Cache-Control": "max-age=86400"})
        
        cached_thumb = get_cached_thumbnail(abs_path)
        if cached_thumb and os.path.exists(cached_thumb):
            return FileResponse(open(cached_thumb, "rb"), content_type="image/jpeg", headers={"Cache-Control": "max-age=86400"})

        # Görev yönetimi
        task_key = f"thumbnail_task:{file_id}"
        task_info = cache.get(task_key)

        if task_info:
            task_id, start_time = task_info
            task = AsyncResult(task_id)
            elapsed_time = time.time() - start_time

            if task.state in ['PENDING', 'STARTED'] and elapsed_time > 300:
                cache.delete(task_key)
            
            elif task.state in ['PENDING', 'STARTED']:
                return Response({"message": "Thumbnail üretiliyor...", "file_id": file_id}, status=202)
            
            elif task.state == 'SUCCESS':
                cache.delete(task_key)
                file.refresh_from_db()
                if file.thumbnail_path and os.path.exists(os.path.join(settings.MEDIA_ROOT, file.thumbnail_path)):
                    return FileResponse(open(os.path.join(settings.MEDIA_ROOT, file.thumbnail_path), "rb"), content_type="image/jpeg", headers={"Cache-Control": "max-age=86400"})

            elif task.state == 'FAILURE':
                # Kritik görev hatasını log dosyası yerine konsola yazdır
                print(f"GÖREV HATASI: Thumbnail görevi başarısız oldu - file_id={file_id}, task_id={task_id}, result={task.result}", file=sys.stderr)
                cache.delete(task_key)
                return Response({"message": "Thumbnail oluşturulamadı."}, status=500)
            else:
                cache.delete(task_key)

        task = generate_thumbnail.delay(file.file_id)
        cache.set(task_key, (task.id, time.time()), timeout=600)

        return Response({"message": "Thumbnail üretimi başlatıldı...", "file_id": file_id}, status=202)
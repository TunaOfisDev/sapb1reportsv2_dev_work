# backend/filesharehub_v2/api/views/directory.py
import os
from urllib.parse import unquote

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from filesharehub_v2.api.permissions import ReadOnlyPermission
from filesharehub_v2.utils.samba_path import secure_join
from filesharehub_v2.utils.fs_scanner import list_directory
from filesharehub_v2.tasks.generate_thumbnail import scan_directory_task


class DirectoryView(APIView):
    """Dizin içeriğini listeler; Celery ile arka planda senkronize eder."""

    permission_classes = [IsAuthenticated, ReadOnlyPermission]

    def get(self, request, *args, **kwargs):
        # 1️⃣ URL‑encoded gelen path'i decode et – "%20" yerine gerçek boşluk kullanırız
        rel_path_encoded = request.query_params.get("path", "")
        rel_path = unquote(rel_path_encoded)

        # 2️⃣ Güvenli tam yol oluştur
        abs_path = secure_join(settings.NETWORK_FOLDER_PATH, rel_path)

        if not os.path.isdir(abs_path):
            return Response({"detail": "Klasör bulunamadı."}, status=404)

        # 3️⃣ Arka planda Celery taramasını tetikle (async)
        try:
            scan_directory_task.delay(abs_path)
        except Exception as exc:
            print(f"[ScanTriggerError] Tarama başlatılamadı: {exc}")

        # 4️⃣ Anlık dizin verisini döndür
        try:
            data = list_directory(abs_path, rel_path)
            return Response(data)
        except Exception as exc:
            return Response({"detail": f"Listeleme hatası: {exc}"}, status=500)

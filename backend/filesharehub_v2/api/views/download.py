# backend/filesharehub_v2/api/views/download.py
import os
from urllib.parse import quote
from django.http import FileResponse, Http404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from filesharehub_v2.api.permissions import ReadOnlyPermission
from filesharehub_v2.utils.samba_path import secure_join
from django.conf import settings

class DownloadView(APIView):
    permission_classes = [IsAuthenticated, ReadOnlyPermission]

    def get(self, request, *args, **kwargs):
        rel_path = request.query_params.get("path")
        if not rel_path:
            raise Http404("Dosya yolu belirtilmedi.")

        abs_path = secure_join(settings.NETWORK_FOLDER_PATH, rel_path)

        if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
            raise Http404("Dosya bulunamadı.")

        filename = os.path.basename(abs_path)
        encoded_filename = quote(filename)

        response = FileResponse(open(abs_path, "rb"), as_attachment=True)
        response["Content-Disposition"] = f"attachment; filename*=UTF-8''{encoded_filename}"
        return response

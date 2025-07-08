# backend/filesharehub/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import StreamingHttpResponse
from django.core.exceptions import PermissionDenied
from ..serializers import FileRecordSerializer, DirectorySerializer
from ..models.models import Directory, FileRecord
from ..utils.rules import is_safe_path, list_directory_contents, file_iterator, is_valid_file_size, should_hide_file
from ..tasks import scan_directory_task
import os
import logging

logger = logging.getLogger(__name__)

BASE_PATH = '/mnt/gorseller'

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB in bytes

class FileListView(APIView):
    def get(self, request, directory_path='', *args, **kwargs):
        base_path = BASE_PATH
        requested_path = os.path.normpath(os.path.join(base_path, directory_path))

        # Güvenlik kontrolü: base_path ile başlayan yollar kabul edilir
        try:
            is_safe_path(base_path, requested_path)
        except PermissionDenied:
            return Response({'detail': 'Invalid path'}, status=status.HTTP_400_BAD_REQUEST)

        # Eğer istenen path bir dosya ise, bu durumda dosya indirme sürecini tetikleriz
        if os.path.isfile(requested_path):
            # Dosya boyutu kontrolü
            if not is_valid_file_size(requested_path):
                return Response({'detail': 'File is too large to download'}, status=status.HTTP_403_FORBIDDEN)

            try:
                response = StreamingHttpResponse(file_iterator(requested_path), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(requested_path)}"'
                response['Content-Length'] = os.path.getsize(requested_path)
                return response
            except PermissionError:
                return Response({'detail': 'Permission denied to access the file'}, status=status.HTTP_403_FORBIDDEN)
            except Exception as e:
                logger.error(f'Error opening file: {e}')
                return Response({'detail': f'Error opening file: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Eğer istenen path bir dizin ise, dizin içeriğini listeleriz
        try:
            if not os.path.exists(requested_path):
                return Response({'detail': f'Path not found: {requested_path}'}, status=status.HTTP_404_NOT_FOUND)
            if not os.path.isdir(requested_path):
                return Response({'detail': f'Provided path is not a directory: {requested_path}'}, status=status.HTTP_400_BAD_REQUEST)

            # Klasör içeriklerini listele ve gizli dosyaları filtrele
            contents = list_directory_contents(requested_path)
            contents['directories'] = [d for d in contents['directories'] if not should_hide_file(d['name'])]
            contents['files'] = [f for f in contents['files'] if not should_hide_file(f['name']) and is_valid_file_size(os.path.join(requested_path, f['name']))]

            # Arka planda dizin tarama görevi başlat (eğer taranması gerekliyse)
            directory = Directory.get_or_create_directory(requested_path)
            if directory.needs_scan():
                scan_directory_task.delay(requested_path)  # Arka plan görevi başlatılır

            return Response(contents, status=status.HTTP_200_OK)

        except PermissionError:
            return Response({'detail': 'Permission denied to access the directory'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f'Error accessing directory: {e}')
            return Response({'detail': f'Error accessing directory: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DirectoryView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            directories = Directory.objects.all()
            serializer = DirectorySerializer(directories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error fetching directories: {e}')
            return Response({'detail': f'Error fetching directories: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FileRecordView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            file_records = FileRecord.objects.all()
            serializer = FileRecordSerializer(file_records, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error fetching file records: {e}')
            return Response({'detail': f'Error fetching file records: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
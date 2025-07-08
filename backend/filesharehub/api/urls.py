# backend/filesharehub/api/urls.py
from django.urls import path
from .views import FileListView, DirectoryView, FileRecordView

app_name = 'filesharehub'

urlpatterns = [
    path('files/', FileListView.as_view(), name='file-list-v1'),
    path('files/<path:directory_path>/', FileListView.as_view(), name='file-list-dynamic-v1'),
    path('directories/', DirectoryView.as_view(), name='directory-list-v1'),
    path('file_records/', FileRecordView.as_view(), name='file-record-list-v1'),

]
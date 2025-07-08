# backend/filesharehub_v2/api/urls.py
from django.urls import path
from filesharehub_v2.api.views.directory import DirectoryView
from filesharehub_v2.api.views.download import DownloadView
from filesharehub_v2.api.views.thumbnail import ThumbnailView

urlpatterns = [
    path("files/", DirectoryView.as_view(), name="file-list-v2"),
    path("download/", DownloadView.as_view(), name="file-download-v2"),
    path("thumb/<int:file_id>/", ThumbnailView.as_view(), name="file-thumbnail-v2"),
    path("thumb/<int:file_id>.jpg", ThumbnailView.as_view(), name="file-thumbnail-jpg-v2"),

]

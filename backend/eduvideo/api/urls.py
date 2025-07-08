# backend/eduvideo/api/views.py
from django.urls import path
from .views import edu_videos_view

urlpatterns = [
    path('videos/', edu_videos_view, name='edu_videos'),
]

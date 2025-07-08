# File: procure_compare/urls.py

from django.urls import path, include

urlpatterns = [
    path("", include("procure_compare.api.urls")),
]

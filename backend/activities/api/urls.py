# backend/activities/api/urls.py
from django.urls import path
from .views import ActivityListView, FetchHanaDataView, APIRootView, export_activities_xlsx

app_name = 'activities'

urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
    path('list/', ActivityListView.as_view(), name='activity-list'),
    path('fetch-hana-data/', FetchHanaDataView.as_view(), name='fetch-hana-activities'),
    path('export-activities-xlsx/', export_activities_xlsx, name='export_activities_xlsx'),
]


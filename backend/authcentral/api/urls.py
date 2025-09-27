# backend/authcentral/urls.py
from django.urls import path
from .views import LoginView, LogoutView, UserView, UserDepartmentsAndPositionsView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


# Diğer URL tanımlamaları
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', UserView.as_view(), name='user'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/validate/', TokenVerifyView.as_view(), name='token_validate'),
    path('user/departments_positions/', UserDepartmentsAndPositionsView.as_view(), name='user_departments_positions'),
]

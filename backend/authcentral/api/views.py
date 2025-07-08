# backend/authcentral/views.py
import logging

from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as SimpleJWTTokenRefreshView

from ..models import BlacklistedToken
from ..serializers import CustomUserSerializer

User = get_user_model()
logger = logging.getLogger(__name__)

class LoginView(APIView):
    """Kullanıcı girişi için JWT token üretir."""
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            logger.info(f"User {email} logged in successfully.")
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        logger.warning(f"Failed login attempt for email: {email}")
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    """Kullanıcıyı çıkış yaptırır ve refresh token'ı kara listeye alır."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            logger.error("No refresh token provided for logout.")
            return Response({'error': 'Refresh token required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            user = User.objects.get(id=token['user_id'])
            BlacklistedToken.objects.create(token=refresh_token, user=user)
            response = Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
            response.delete_cookie("refresh_token")
            logger.info(f"User {user.email} logged out successfully.")
            return response
        except TokenError as e:
            logger.exception(f"Invalid token during logout: {e}")
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            logger.error("User not found for provided token.")
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

class UserView(APIView):
    """Oturum açmış kullanıcının bilgilerini döndürür."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        logger.info(f"User {request.user.email} profile accessed.")
        return Response(serializer.data)

class TokenVerifyView(APIView):
    """Access token'ın geçerliliğini kontrol eder."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get('token')
        if not token:
            logger.error("No token provided for verification.")
            return Response({'error': 'Token required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            valid_data = AccessToken(token)
            valid_data.check_exp()
            logger.info("Token verified successfully.")
            return Response({'token': 'Valid'})
        except TokenError as e:
            logger.exception(f"Token verification failed: {e}")
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)

class TokenRefreshView(SimpleJWTTokenRefreshView):
    """Refresh token ile yeni access token üretir."""
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            logger.error("No refresh token provided for refresh.")
            return Response({'error': 'Refresh token required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = super().post(request, *args, **kwargs)
            logger.info("Token refreshed successfully.")
            return response
        except TokenError as e:
            logger.exception(f"Token refresh failed: {e}")
            if isinstance(e, InvalidToken):
                try:
                    RefreshToken(refresh_token).check_exp()
                except TokenError as sub_e:
                    logger.error(f"Refresh token expired: {sub_e}")
                    return Response(
                        {'error': 'Refresh token has expired. Please login again.'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                return Response(
                    {'error': 'Invalid refresh token. Please login again.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            return Response(
                {'error': 'Invalid or expired token. Please login again.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

class UserDepartmentsAndPositionsView(APIView):
    """Kullanıcının departman ve pozisyonlarını listeler."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        departments = request.user.departments.all()
        positions = request.user.positions.all()
        department_names = [dept.name for dept in departments]
        position_names = [pos.name for pos in positions]
        logger.info(f"Departments and positions accessed for user {request.user.email}")
        return Response({'departments': department_names, 'positions': position_names})
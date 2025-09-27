# backend/crmblog/api/views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from ..serializers import PostSerializer
from ..models.models import Post
from django.contrib.auth import get_user_model
from ..permissions import HasCRMBlogAccess  # CRM Blog API izin sınıfını ekliyoruz

User = get_user_model()

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, HasCRMBlogAccess]  # İzin sınıfları ekleniyor

    def perform_create(self, serializer):
        """
        Yeni bir post oluştururken yetki kontrolü yapılır ve yetkisiz ise hata fırlatılır.
        """
        if not self.request.user.has_perm('crmblog.add_post'):
            raise PermissionDenied(detail="Yeni bir post oluşturmak için yetkiniz yok. Lütfen yöneticiyle iletişime geçin.")
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """
        Post güncellenirken yetki kontrolü yapılır ve yetkisiz ise hata fırlatılır.
        """
        if not self.request.user.has_perm('crmblog.change_post'):
            raise PermissionDenied(detail="Postu güncellemek için yetkiniz yok. Lütfen yöneticiyle iletişime geçin.")
        serializer.save()

    def perform_destroy(self, instance):
        """
        Post silinirken yetki kontrolü yapılır ve yetkisiz ise hata fırlatılır.
        """
        if not self.request.user.has_perm('crmblog.delete_post'):
            raise PermissionDenied(detail="Postu silmek için yetkiniz yok. Lütfen yöneticiyle iletişime geçin.")
        instance.delete()

    def get_queryset(self):
        user = self.request.user

        # Genel Müdür, Yönetim ve Bilgi Sistem departmanlarının ID'leri
        privileged_departments = [3, 2, 1]
        # Kullanıcının departman ID'lerini al
        user_departments = user.departments.values_list('id', flat=True)

        # Eğer kullanıcı özel bir departmanda ise tüm görevleri görür
        if any(dept in privileged_departments for dept in user_departments):
            return Post.objects.all()

        # Belirli kullanıcılar için departman postları gösterme
        if user.id == 204:  # Arge departman lideri için
            department_members = User.objects.filter(departments__id=9)  # Arge departmanının ID'si
            return Post.objects.filter(author__in=department_members)

        # Aksi takdirde sadece kullanıcının görevlerini görür
        return Post.objects.filter(author=user)

    def handle_exception(self, exc):
        """
        Hataları özelleştirmek için handle_exception metodu.
        """
        if isinstance(exc, PermissionDenied):
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return super().handle_exception(exc)






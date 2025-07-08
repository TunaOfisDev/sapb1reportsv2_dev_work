# path: backend/stockcardintegration/api/helptext_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..models.helptext import FieldHelpText
from .serializers import FieldHelpTextSerializer


class FieldHelpTextListView(APIView):
    """
    Form alanları için açıklama metinlerini döner.
    - `GET` → Tüm field helptext tanımlarını getirir.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        helptexts = FieldHelpText.objects.all().order_by("field_name")
        serializer = FieldHelpTextSerializer(helptexts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

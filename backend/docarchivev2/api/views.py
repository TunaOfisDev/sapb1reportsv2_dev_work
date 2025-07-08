# backend/docarchivev2/api/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from ..models.models import Department, Document, DocumentFile
from ..serializers import DepartmentSerializer, DocumentSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)  # JSONParser eklenmiş olabilir

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            document = serializer.save()

            # Dosya yüklemesi için ek işlemler
            files = request.FILES.getlist('file')  # 'file' anahtarına göre dosyaları al
            for file in files:
                DocumentFile.objects.create(document=document, file=file)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





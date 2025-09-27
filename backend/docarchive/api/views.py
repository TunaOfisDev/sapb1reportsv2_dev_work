# backend/docarchive/api/views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from ..models.models import Document, Department, DocumentFile
from ..serializers import DocumentSerializer, DepartmentSerializer, DocumentFileSerializer

class DocumentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DocumentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)



# Department için yeni view'lar ekliyoruz
class DepartmentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class DepartmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class DocumentFileListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DocumentFileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Belirli bir belgeye ait dosyaları döndürür.
        """
        document_id = self.kwargs.get('document_id')
        if document_id:
            return DocumentFile.objects.filter(document_id=document_id)
        return DocumentFile.objects.none()

    def post(self, request, *args, **kwargs):
        # Serializer'ı istek verisi ile başlat
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Serializer geçerliyse, veriyi kaydet
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Serializer geçerli değilse, hataları dön
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class DocumentFileDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DocumentFile.objects.all()
    serializer_class = DocumentFileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

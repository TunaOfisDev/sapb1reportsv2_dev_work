# backend/docarchivev2/models/models.py
from django.db import models
from .base import BaseModel
from django.utils.timezone import now

def document_upload_path(instance, filename):
    # Belgenin ait olduğu klasör yolu
    directory = instance.document.id if instance.document.id is not None else f'temp_{now().strftime("%Y%m%d%H%M%S")}'
    return f'backend/media/documents/{directory}/{filename}'

class Department(BaseModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Document(BaseModel):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    owner_name = models.CharField(max_length=255, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')

    def __str__(self):
        return self.name

class DocumentFile(BaseModel):
    document = models.ForeignKey(Document, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to=document_upload_path)

    def __str__(self):
        return f'File for {self.document.name}'

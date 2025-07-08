# path: backend/stockcardintegration/models/helptext.py

from django.db import models
from .base import BaseModel

class FieldHelpText(BaseModel):  #  BaseModel kalıtımı eklendi
    field_name = models.CharField(max_length=100, unique=True)  # örn: "ItemCode"
    label = models.CharField(max_length=100)  # örn: "Kalem Kodu"
    description = models.TextField()  # örn: "Boşluk içeremez, max 50 karakter..."

    def __str__(self):
        return f"{self.label} ({self.field_name})"


    class Meta:
        ordering = ["id"]        # 🔑 A-Z sıralama
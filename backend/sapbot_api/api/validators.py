# backend/sapbot_api/api/validators.py
"""API seviyesinde kullanilan validator'lar"""

from django.core.files.uploadedfile import UploadedFile

from sapbot_api.utils.validators import BaseValidator, ChatMessageValidator


class DocumentFileValidator(BaseValidator):
    """Yüklenen dosyalar için basit kontrol"""

    max_size = 20 * 1024 * 1024  # 20MB

    def validate(self, value: UploadedFile) -> UploadedFile:
        if not isinstance(value, UploadedFile):
            self.raise_error("Geçersiz dosya", "file")
        if value.size > self.max_size:
            self.raise_error(
                "Dosya boyutu sınırı aşıldı",
                field="file_size",
                value=value.size,
            )
        return value


__all__ = [
    "ChatMessageValidator",
    "DocumentFileValidator",
]
 

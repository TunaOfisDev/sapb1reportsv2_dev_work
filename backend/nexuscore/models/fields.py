# path: /var/www/sapb1reportsv2/backend/nexuscore/models/fields.py

import json
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from cryptography.fernet import Fernet, InvalidToken

# Ayarlardaki anahtarı kullanarak bir şifreleme nesnesi oluşturalım.
# settings.py dosyanızda FERNET_KEY olduğundan emin olun. 
# Önceki adımlarda bunu eklemiştik: FIELD_ENCRYPTION_KEYS = [config('FERNET_KEY')]
# django-cryptography list formatını bekliyordu, şimdi direkt anahtara dönelim.
# settings.py -> FERNET_KEY = config('FERNET_KEY')
fernet = Fernet(settings.FERNET_KEY.encode())

class EncryptedJSONField(models.JSONField):
    """
    JSON verilerini veritabanına yazmadan önce şifreleyen ve okurken şifresini
    çözen, tamamen kendimize ait, güvenli bir model alanı.
    """
    def get_prep_value(self, value):
        """Model verisini veritabanına yazılacak formata hazırlar."""
        if value is None:
            return None
        
        # Standart JSONField'in yaptığı gibi, veriyi JSON string'ine çevir.
        json_string = super().get_prep_value(value)
        
        # JSON string'ini şifrele.
        encrypted_value = fernet.encrypt(json_string.encode('utf-8'))
        
        return encrypted_value.decode('utf-8')

    def from_db_value(self, value, expression, connection):
        """Veritabanından gelen veriyi Python formatına dönüştürür."""
        if value is None:
            return None
        
        try:
            # Veritabanından gelen şifreli metnin şifresini çöz.
            decrypted_bytes = fernet.decrypt(value.encode('utf-8'))
            json_string = decrypted_bytes.decode('utf-8')
            
            # Standart JSONField'in yaptığı gibi, JSON string'ini Python nesnesine çevir.
            return super().from_db_value(json_string, expression, connection)
        
        except InvalidToken:
            # Eğer veri çözülemezse (örn: eski, şifresiz veri), hata vermek yerine
            # boş bir sözlük döndürerek sistemi daha esnek hale getirebiliriz.
            # Veya bir ValidationError fırlatabiliriz.
            raise ValidationError("Şifreli veri bozuk veya geçersiz.")
# path: backend/nexuscore/fields.py

import json
import logging
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

if not hasattr(settings, 'FERNET_KEY'):
    raise RuntimeError("settings.py dosyasında FERNET_KEY tanımlanmamış!")
try:
    fernet = Fernet(settings.FERNET_KEY.encode())
except (ValueError, TypeError):
    raise RuntimeError("settings.py'deki FERNET_KEY geçerli bir Fernet anahtarı değil!")

class EncryptedJSONField(models.JSONField):
    """
    JSON verilerini veritabanına yazmadan önce şifreleyen ve okurken şifresini
    çözen, tamamen kendimize ait, güvenli ve sağlam bir model alanı.
    """
    def get_prep_value(self, value):
        if value is None:
            return value
        
        # ### NİHAİ DÜZELTME BURADA ###
        # Gelen değerin türünü kontrol ediyoruz. Eğer metin değilse (örn: dict),
        # onu güvenli bir şekilde JSON metnine dönüştürüyoruz.
        if not isinstance(value, str):
            value = json.dumps(value)
        
        # Artık 'value' değişkeninin kesinlikle bir string olduğunu biliyoruz.
        try:
            encrypted_bytes = fernet.encrypt(value.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"EncryptedJSONField şifreleme hatası: {e}")
            raise ValidationError("Veri şifrelenirken bir hata oluştu.")

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        
        try:
            decrypted_bytes = fernet.decrypt(value.encode('utf-8'))
            json_string = decrypted_bytes.decode('utf-8')
            return json.loads(json_string)
        except InvalidToken:
            logger.warning(f"Geçersiz şifreli veri bulundu (InvalidToken): '{str(value)[:20]}...'")
            return None
        except Exception as e:
            logger.error(f"EncryptedJSONField şifre çözme hatası: {e}")
            return None
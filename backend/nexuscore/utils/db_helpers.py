# path: /var/www/sapb_reports_v2/backend/nexuscore/utils/db_helpers.py

import re
from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError, ProgrammingError

def generate_db_alias(title: str) -> str:
    """
    Kullanıcının girdiği başlığı, Django'nun DATABASES ayarlarında
    güvenle kullanılabilecek bir takma isme (alias) dönüştürür.
    Örn: "Üretim SQL Sunucusu!" -> "dyn_uretim_sql_sunucusu"
    """
    # Harf, rakam veya alt çizgi olmayan her şeyi alt çizgi ile değiştir
    s = re.sub(r'[^a-zA-Z0-9_]', '_', title)
    # Birden fazla alt çizgiyi tek alt çizgiye indir
    s = re.sub(r'__+', '_', s.lower())
    # Django'nun dahili alias'ları ile çakışmayı önlemek için bir önek ekleyelim.
    return f"dyn_{s}"

def test_database_connection(config: dict) -> tuple[bool, str]:
    """
    Verilen bir veri tabanı yapılandırmasını (config) test eder.
    Bağlantıyı hafızada (in-memory) geçici olarak oluşturur,
    bir test sorgusu çalıştırır ve başarılı/başarısız durumunu
    bir mesajla birlikte döndürür. En önemlisi, işlemden sonra
    arkasında iz bırakmaz, tüm geçici bağlantıyı temizler.

    Args:
        config (dict): Django'nun DATABASES sözlüğüyle uyumlu yapılandırma.

    Returns:
        tuple[bool, str]: (Başarı Durumu, Mesaj)
    """
    # Her test için benzersiz ve geçici bir alias oluşturalım.
    temp_alias = "nexus_core_test_connection"
    
    try:
        # 1. Adım: Yapılandırmayı Django'nun ayar sözlüğüne anlık olarak ekle.
        # Bu, diske hiçbir şey yazmaz, sadece o anki oturumun hafızasını etkiler.
        settings.DATABASES[temp_alias] = config

        # 2. Adım: Django'nun bağlantı yöneticisini kullanarak bağlantıyı kurmayı dene.
        # En basit ve evrensel test sorgusu "SELECT 1" dir.
        with connections[temp_alias].cursor() as cursor:
            cursor.execute("SELECT 1;")
            # Eğer buraya kadar hata almadıysak, bağlantı başarılıdır.
        
        return True, "Veri tabanı bağlantısı başarıyla doğrulandı."

    except OperationalError as e:
        # En yaygın hata: Host bulunamadı, şifre yanlış, port kapalı vb.
        return False, f"Bağlantı Hatası: Kimlik bilgileri veya sunucu erişiminde sorun var. Detay: {e}"
    
    except ProgrammingError as e:
        # Genellikle veritabanı adı yanlış olduğunda veya yetki olmadığında ortaya çıkar.
        return False, f"Yapılandırma Hatası: Veri tabanı adı bulunamadı veya erişim yetkisi yok. Detay: {e}"
        
    except Exception as e:
        # Beklenmedik diğer tüm hatalar için.
        return False, f"Beklenmedik bir hata oluştu: {e}"
        
    finally:
        # 3. Adım (En Kritik Adım): Ne olursa olsun temizlik yap!
        # `finally` bloğu, try içinde hata olsa da olmasa da çalışır.
        # Bu, sistemde artık bağlantılar bırakmamamızı garanti eder.
        if temp_alias in connections:
            connections[temp_alias].close()
        if temp_alias in settings.DATABASES:
            del settings.DATABASES[temp_alias]
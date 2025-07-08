"""
SAPB1ReportsV2 – Merkezi Loguru Yapılandırması
================================================
Bu dosya projenin **kurumsal** loglama standartlarını tek merkezde toplar.

📝 İşlevleri
-------------
1. **logs** klasörünü (yoksa) oluşturur.
2. Her mantıksal uygulama bileşeni için *tek bir* log dosyası ve filtre tanımlar – böylece
   farklı modüllerin hataları birbirinin dosyasına karışmaz.
3. Modüllerin kolay kullanımı için `get_logger()` yardımcı fonksiyonu sunar.

Kullanım Örneği
---------------
```python
from logger_config import get_logger

logger = get_logger(__name__)
logger.error("Bir şeyler ters gitti!")
```
"""

import os
from loguru import logger
from datetime import timedelta

# 🔧 1) Log klasörünün yolu
BASE_DIR = os.path.dirname(__file__)
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Klasör yoksa oluştur
os.makedirs(LOG_DIR, exist_ok=True)

# 🔧 2) Hangi modül hangi dosyaya yazacak?
#    "module" alanı filtre için kullanılır (startswith kontrolü).
LOG_SINKS = {
    "backend":            {"file": "backend.log",           "module": "backend"},
    "celery":             {"file": "celery.log",            "module": "celery"},
    "celerybeat":         {"file": "celerybeat.log",        "module": "celery.beat"},
    "db_backup":          {"file": "db_backup.log",         "module": "postgresqldb_backup"},
    "gunicorn": {"file": "gunicorn.log", "module": "gunicorn"},
    "hanadb_integration": {"file": "hanadb_integration.log", "module": "hanadb.integration"},
    "hanadb":             {"file": "hanadb.log",            "module": "hanadb"},
    "productconfig":      {"file": "productconfig.log",     "module": "productconfig"},
    "report_orchestrator":{"file": "report_orchestrator.log","module": "report_orchestrator"},
    "sapreports":         {"file": "sapreports.log",        "module": "sapreports"},
    "stockcard":          {"file": "stockcard_integration.log","module": "stockcard_integration"},
}

# 🔧 3) Önce tüm mevcut Loguru sink'lerini kaldır
logger.remove()

# 🔧 4) Filtre oluşturucu
def _filtre_uret(modul_adi: str):
    """Kayıt modül adı istenen önekle başlıyorsa True döndür."""
    def _filtre(kayit):
        return kayit["name"].startswith(modul_adi)
    return _filtre

# 🔧 5) Her sink'i ekle
for key, meta in LOG_SINKS.items():
    dosya_yolu = os.path.join(LOG_DIR, meta["file"])
    logger.add(
        dosya_yolu,
        level="ERROR",                 # Sadece ERROR ve üstü
        rotation=1 * 1024 * 1024,  # 1 MB
        retention=0,  # biriktirme yok, eskisinin üstüne yaz
        enqueue=True,                  # Çok iş parçacıklı güvenli kuyruğa alma
        backtrace=False,
        diagnose=False,
        filter=_filtre_uret(meta["module"]),
    )

# 🔧 6) Genel/fallback hatalar için tek dosya (son savunma hattı)
logger.add(
    os.path.join(LOG_DIR, "_other_errors.log"),
    level="ERROR",
    rotation=1 * 1024 * 1024,  # 1 MB
    retention=0,  # biriktirme yok, eskisinin üstüne yaz
    enqueue=True,
    backtrace=False,
    diagnose=False,
)

# 🎁 7) Yardımcı fonksiyon

def get_logger(modul_adi: str):
    """Verilen modül adına bağlı Loguru logger nesnesi döndürür."""
    return logger.bind(name=modul_adi)

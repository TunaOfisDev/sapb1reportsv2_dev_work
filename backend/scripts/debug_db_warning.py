#!/usr/bin/env python3
"""
🚦  debug_db_warning.py ─ SAPB1ReportsV2
────────────────────────────────────────
Amaç
=====
* Django uygulaması start‑up aşamasında görülen 
  **RuntimeWarning: Accessing the database during app initialization...**
  uyarısının hangi **modül, fonksiyon ve satır** tarafından tetiklendiğini
  kesin olarak bulmak.

Özellikler
----------
1. `warnings.showwarning` hook'u Override edilerek sadece **RuntimeWarning**
   mesajları yakalanır.
2. Uyarı oluştuğunda **5 satırlık stack‑trace** terminale basılır – böylece
   hatalı `ready()` veya module‑level sorgu hemen ortaya çıkar.
3. Proje kök dizini **otomatik** olarak `PYTHONPATH`'e eklenir; `DJANGO_SETTINGS_MODULE`
   ise `sapreports.settings` olarak ayarlanır.

Kullanım
--------
```bash
$ cd /var/www/sapb1reportsv2/backend
$ python scripts/debug_db_warning.py
```
Script başarıyla biterse hiçbir çıktı vermez; uyarı oluştuğunda nedenini ve
kaynağını termianlde görebilirsin.
"""

import os
import sys
import traceback
import warnings
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# 1) Proje kök dizinini PYTHONPATH'e ekle
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# ─────────────────────────────────────────────────────────────────────────────
# 2) Django ayarlarını işaretle
# ─────────────────────────────────────────────────────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sapreports.settings")

# ─────────────────────────────────────────────────────────────────────────────
# 3) Warnings hook'u tanımla
# ─────────────────────────────────────────────────────────────────────────────


def _show_warning(msg, cat, filename, lineno, file=None, line=None):
    if issubclass(cat, RuntimeWarning) and "App initialization" in str(msg):
        banner = "\n⚠️  RuntimeWarning yakalandı".ljust(80, "-")
        print(banner)
        print(f"Mesaj   : {msg}")
        print(f"Kaynak  : {filename}:{lineno}\n")
        traceback.print_stack(limit=5)
        print("-" * 80)


warnings.showwarning = _show_warning

# ─────────────────────────────────────────────────────────────────────────────
# 4) Django'yu başlat (uyarı tetiklenirse yukarıdaki hook devreye girer)
# ─────────────────────────────────────────────────────────────────────────────

try:
    import django
    django.setup()
except Exception as exc:
    print(f"Django başlatılırken hata oluştu: {exc}")
    sys.exit(1)

print("✅ Django sorunsuz başlatıldı – uyarı oluşmadı.")



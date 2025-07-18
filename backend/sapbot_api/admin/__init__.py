# backend/sapbot_api/admin/__init__.py
"""
SAPBot API – Django-Admin paket başlangıç modülü

• Bütün alt admin modüllerini içeri aktarır (import-side-effect ile ModelAdmin
  sınıflarını kaydeder).
• Ortak admin özelleştirmelerini (logo, başlık, site_url …) tek noktadan uygular.
"""

# ---------------------------------------------------------------------------
# 1) Ortak admin başlık / tema ayarları
# ---------------------------------------------------------------------------
from .base_admin import customize_admin_site  # noqa: E402

# ---------------------------------------------------------------------------
# 2) Alt-modüllerin importu
#    NOT: Yalnızca import işlemi yeterli; ModelAdmin sınıfları kayıt olur.
# ---------------------------------------------------------------------------
from .system_admin import *    # noqa: F401,F403
from .user_admin import *      # noqa: F401,F403
from .analytics_admin import * # noqa: F401,F403
from .chat_admin import *      # noqa: F401,F403
from .document_admin import *  # noqa: F401,F403

# ---------------------------------------------------------------------------
# 3) Admin site kişiselleştirme (başlık vb.)
# ---------------------------------------------------------------------------
customize_admin_site()

# İsteğe bağlı dışa aktarım: hangi modülleri “public” yapmak istediğinizi belirtin
__all__ = [
    # alt modüllerin __all__ listelerindeki elemanlar zaten eksport edilir
    # ama buraya eklemeniz kod tamamlama araçlarına yardımcı olur
    *globals().keys()
]

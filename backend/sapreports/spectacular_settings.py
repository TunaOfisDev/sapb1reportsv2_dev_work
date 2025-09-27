# backend/sapreports/spectacular_settings.py
"""
DRF Spectacular – OpenAPI/Swagger konfigürasyonu
"""

SPECTACULAR_SETTINGS = {
    "TITLE": "SAPB1Reports V2 API Dokümantasyonu",
    "DESCRIPTION": (
        "SAP Business One HANA ve LOGO MS SQL verilerini entegre eden "
        "kurumsal raporlama servisleri.\n\n"
        "🔐 JWT Bearer doğrulaması  \n"
        "📄 Tüm çıkışlar JSON  \n\n"
        "Geliştirici: **Selim Koçak**  \n"
        "E-posta: selim.kocak@tunacelik.com.tr  \n"
        "Telefon: +90 532 793 90 62"
    ),
    "VERSION": "2.0.0",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAdminUser"],
}

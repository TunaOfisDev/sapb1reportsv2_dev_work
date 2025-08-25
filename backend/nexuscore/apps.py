
# path: /var/www/sapb1reportsv2/backend/nexuscore/apps.py

from django.apps import AppConfig

class NexusCoreConfig(AppConfig):
    """
    Nexus Core uygulamasının yapılandırma sınıfı.
    Bu sınıf, Django projesine uygulamamızın meta verilerini sağlar.
    """
    
    # Django 64-bit ID alanlarını varsayılan olarak kullanır. Bu modern ve en iyi pratiktir.
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Uygulamanın Python path'i. Django'nun uygulamayı bulması için gereklidir.
    name = 'nexuscore'
    
    # Django Admin panelinde görünecek olan, insan tarafından okunabilir, güzel isim.
    # Bu, projemize profesyonel bir dokunuş katar.
    verbose_name = "Nexus Core - Dinamik Veri Çekirdeği"
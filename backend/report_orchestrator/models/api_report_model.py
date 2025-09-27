# backend/report_orchestrator/models/api_report_model.py

from django.db import models
from django.db.models import JSONField


class APIReportModel(models.Model):
    """
    Her sabah çalışan, veri çeken, filtreleyen, sıralayan ve
    çıktısını hazırlayan otomatik rapor motoru için yapılandırma modelidir.
    """

    MODE_CHOICES = [
        ('passive', 'Pasif (ham veriyi al + filtrele)'),
        ('active', 'Aktif (veriyi tetikle + bekle + özet veriyi al)'),
    ]

    api_name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Bu rapora özel kısa sistem adı (örn. 'balance_top10')"
    )

    mode = models.CharField(
        max_length=10,
        choices=MODE_CHOICES,
        default='passive',
        help_text="Rapor modu: pasif veya aktif tetikleyicili yapı"
    )

    trigger_url = models.URLField(
        blank=True,
        null=True,
        help_text="Aktif modda veriyi tetiklemek için kullanılacak endpoint"
    )

    data_pull_url = models.URLField(
        help_text="Veriyi çekeceğimiz canlı endpoint (aktif modda özet veriyi verir)"
    )

    wait_seconds = models.IntegerField(
        default=300,
        help_text="Tetikleme sonrası bekleme süresi (aktif mod için saniye cinsinden)"
    )

    rule_json = JSONField(
        default=dict,
        help_text="Veri üzerinde sıralama, filtreleme, limit ve doğrulama kuralları"
    )

    result_json = JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="İşlenmiş, doğrulanmış ve sisteme kaydedilmiş özet veri"
    )

    last_error_message = models.TextField(
        blank=True,
        null=True,
        help_text="Son hata mesajı (varsa)"
    )

    last_run_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Son başarılı çalıştırma zamanı"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Bu rapor aktif mi? (pasif yapılırsa sabah çalışmaz)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "API Rapor Modeli"
        verbose_name_plural = "API Rapor Modelleri"

    def __str__(self):
        return f"[{self.api_name}] – {self.get_mode_display()}"

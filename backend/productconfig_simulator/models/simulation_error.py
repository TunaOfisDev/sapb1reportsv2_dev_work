# backend/productconfig_simulator/models/simulation_error.py
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import JSONField
from django.conf import settings

from .base import SimulatorBaseModel
from productconfig.models import ProductModel, Question, Option
from .simulation_job import SimulationJob

class SimulationError(SimulatorBaseModel):
    """
    Simülasyon sırasında tespit edilen hataları ve sorunları kaydeden model.
    """
    class ErrorType(models.TextChoices):
        MISSING_OPTIONS = 'missing_options', _('Seçeneği Eksik Soru')
        DEPENDENT_RULE_ERROR = 'dependent_rule_error', _('Bağımlı Kural Hatası')
        CONDITIONAL_OPTION_ERROR = 'conditional_option_error', _('Koşullu Seçenek Hatası')
        PRICE_MULTIPLIER_ERROR = 'price_multiplier_error', _('Fiyat Çarpan Hatası')
        PROCESSING_ERROR = 'processing_error', _('İşlem Hatası')
        DATA_INCONSISTENCY = 'data_inconsistency', _('Veri Tutarsızlığı')
    
    class ErrorSeverity(models.TextChoices):
        INFO = 'info', _('Bilgi')
        WARNING = 'warning', _('Uyarı')
        ERROR = 'error', _('Hata')
        CRITICAL = 'critical', _('Kritik')
    
    simulation = models.ForeignKey(
        SimulationJob,
        on_delete=models.CASCADE,
        related_name='errors',
        verbose_name=_("Simülasyon")
    )
    
    error_type = models.CharField(
        max_length=30,
        choices=ErrorType.choices,
        verbose_name=_("Hata Tipi")
    )
    
    severity = models.CharField(
        max_length=10,
        choices=ErrorSeverity.choices,
        default=ErrorSeverity.ERROR,
        verbose_name=_("Önem Derecesi")
    )
    
    message = models.TextField(
        verbose_name=_("Hata Mesajı")
    )
    
    details = JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Detaylar")
    )
    
    # İlgili objeler (opsiyonel)
    product_model = models.ForeignKey(
        ProductModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='simulation_errors',
        verbose_name=_("Ürün Modeli")
    )
    
    question = models.ForeignKey(
        Question,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='simulation_errors',
        verbose_name=_("Soru")
    )
    
    option = models.ForeignKey(
        Option,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='simulation_errors',
        verbose_name=_("Seçenek")
    )
    
    resolution_status = models.BooleanField(
        default=False,
        verbose_name=_("Çözüldü mü?")
    )
    
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_simulation_errors',
        verbose_name=_("Çözen Kullanıcı")
    )
    
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Çözülme Zamanı")
    )
    
    resolution_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Çözüm Notları")
    )
    
    class Meta:
        verbose_name = _("Simülasyon Hatası")
        verbose_name_plural = _("Simülasyon Hataları")
        ordering = ['-created_at', 'severity']
        indexes = [
            models.Index(fields=['simulation', 'error_type']),
            models.Index(fields=['resolution_status']),
            models.Index(fields=['product_model']),
        ]
    
    def __str__(self):
        return f"{self.get_error_type_display()} - {self.message[:50]}..."
    
    def resolve(self, user=None, notes=None):
        """Hatayı çözüldü olarak işaretler"""
        self.resolution_status = True
        self.resolved_by = user
        self.resolved_at = timezone.now()
        if notes:
            self.resolution_notes = notes
        self.save()
    
    @classmethod
    def create_missing_options_error(cls, simulation, question, product_model=None):
        """Seçeneği eksik olan soru için hata kaydı oluşturur"""
        return cls.objects.create(
            simulation=simulation,
            error_type=cls.ErrorType.MISSING_OPTIONS,
            severity=cls.ErrorSeverity.ERROR,
            message=f"Soru '{question.name}' için hiç seçenek tanımlanmamış",
            question=question,
            product_model=product_model,
            details={
                'question_id': question.id,
                'question_name': question.name,
                'question_type': question.question_type,
                'product_model_id': product_model.id if product_model else None,
                'product_model_name': product_model.name if product_model else None,
            }
        )
    
    @classmethod
    def create_dependent_rule_error(cls, simulation, rule, message, product_model=None):
        """Bağımlı kural hatası için kayıt oluşturur"""
        return cls.objects.create(
            simulation=simulation,
            error_type=cls.ErrorType.DEPENDENT_RULE_ERROR,
            severity=cls.ErrorSeverity.ERROR,
            message=message,
            question=rule.parent_question,
            product_model=product_model,
            details={
                'rule_id': rule.id,
                'rule_name': rule.name,
                'rule_type': rule.rule_type,
                'parent_question_id': rule.parent_question.id,
                'parent_question_name': rule.parent_question.name,
                'trigger_option_id': rule.trigger_option.id,
                'trigger_option_name': rule.trigger_option.name,
                'product_model_id': product_model.id if product_model else None,
                'product_model_name': product_model.name if product_model else None,
            }
        )
    
    @classmethod
    def create_processing_error(cls, simulation, error_message, product_model=None, question=None, option=None):
        """Genel işlem hatası için kayıt oluşturur"""
        return cls.objects.create(
            simulation=simulation,
            error_type=cls.ErrorType.PROCESSING_ERROR,
            severity=cls.ErrorSeverity.ERROR,
            message=error_message,
            product_model=product_model,
            question=question,
            option=option,
            details={
                'product_model_id': product_model.id if product_model else None,
                'product_model_name': product_model.name if product_model else None,
                'question_id': question.id if question else None,
                'question_name': question.name if question else None,
                'option_id': option.id if option else None,
                'option_name': option.name if option else None,
            }
        )
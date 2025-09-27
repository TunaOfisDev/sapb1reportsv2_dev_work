# backend/productconfig/models/price_multiplier_rule.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from .base import BaseModel
from .option import Option

class PriceMultiplierRule(BaseModel):
    """
    Seçenekler arası fiyat çarpanı ilişkilerini yöneten model.
    Belirli seçenek kombinasyonları için fiyat çarpanları tanımlar.
    """
    
    class LogicalOperator(models.TextChoices):
        AND = 'and', _('VE (Tüm seçenekler seçilmeli)')
        OR = 'or', _('VEYA (Herhangi biri seçilebilir)')

    name = models.CharField(
        max_length=255,
        verbose_name=_("Kural Adı"),
        help_text=_("Kuralı tanımlayan benzersiz isim")
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("Açıklama"),
        help_text=_("Kural hakkında detaylı açıklama")
    )

    # ForeignKey yerine ManyToManyField olarak değişti
    target_options = models.ManyToManyField(
        Option,
        related_name='price_multiplier_rules_as_target',
        verbose_name=_("Hedef Seçenekler"),
        help_text=_("Fiyatı çarpan ile değişecek seçenekler")
    )

    trigger_options = models.ManyToManyField(
        Option,
        related_name='triggering_rules',
        verbose_name=_("Tetikleyici Seçenekler"),
        help_text=_("Bu seçenekler seçildiğinde kural tetiklenir")
    )

    multiplier_factor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0.01),
            MaxValueValidator(100.00)
        ],
        verbose_name=_("Çarpan Faktörü"),
        help_text=_("Hedef seçeneğin fiyatı bu değer ile çarpılacak (0.01-100.00)")
    )

    min_trigger_count = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        verbose_name=_("Minimum Tetikleyici Sayısı"),
        help_text=_("Kuralın tetiklenmesi için gereken minimum seçenek sayısı")
    )

    logical_operator = models.CharField(
        max_length=3,
        choices=LogicalOperator.choices,
        default=LogicalOperator.AND,
        verbose_name=_("Mantıksal Operatör"),
        help_text=_("Tetikleyici seçeneklerin nasıl değerlendirileceğini belirler")
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Sıra"),
        help_text=_("Kuralların değerlendirilme sırası")
    )

    class Meta:
        verbose_name = _("07-Fiyat Çarpan Kuralı")
        verbose_name_plural = _("07-Fiyat Çarpan Kuralları")
        ordering = ['order', 'name']
        

    def __str__(self):
        if not self.id:  # Nesne henüz kaydedilmemişse
            return self.name

        try:
            target_names = ", ".join([option.name for option in self.target_options.all()[:5]])
            return f"{self.name} - [{target_names}] (x{self.multiplier_factor})"
        except RecursionError:
            return f"{self.name} - Recursive Error Detected"


    def evaluate(self, selected_option_ids: list) -> tuple:
        """
        Seçili seçenekler için kuralı değerlendirir.
        
        Args:
            selected_option_ids (list): Seçili seçenek ID'leri listesi
            
        Returns:
            tuple: (bool, Decimal) - (Kural tetiklendi mi?, Uygulanacak çarpan)
        """
        if not selected_option_ids:
            return False, 1

        trigger_option_ids = set(self.trigger_options.values_list('id', flat=True))
        selected_ids = set(selected_option_ids)
        common_options = trigger_option_ids.intersection(selected_ids)
        
        if len(common_options) < self.min_trigger_count:
            return False, 1

        if self.logical_operator == self.LogicalOperator.AND:
            is_triggered = trigger_option_ids.issubset(selected_ids)
        else:  
            is_triggered = len(common_options) >= self.min_trigger_count

        return is_triggered, self.multiplier_factor if is_triggered else 1

    def clean(self):
        from django.core.exceptions import ValidationError

        if not self.id:  # Kaydedilmemiş nesneler için erken çıkış
            return

        trigger_ids = set(self.trigger_options.values_list('id', flat=True))
        target_ids = set(self.target_options.values_list('id', flat=True))

        # Tetikleyici seçenekler hedeflerle çakışıyorsa
        if trigger_ids.intersection(target_ids):
            raise ValidationError("Hedef seçenekler tetikleyici seçenekler arasında olamaz.")

        # Minimum tetikleyici sayısı
        if len(trigger_ids) < self.min_trigger_count:
            raise ValidationError(
                f"Minimum {self.min_trigger_count} tetikleyici seçenek gerekiyor."
            )


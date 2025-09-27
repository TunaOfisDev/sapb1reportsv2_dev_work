# dosya path yolu: backend/productconfig/models/conditional_options.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import BaseModel  # Sizin mevcut base modeliniz
from .option import Option  # Seçenek modeli
from .question import Question  # Soru modeli

class ConditionalOption(BaseModel):
    """
    Koşullu seçenekleri tanımlar. Kullanıcı hangi seçenekleri seçerse, 
    o seçeneklere göre hangi seçeneklerin tetikleneceğini belirler.
    """

    class DisplayMode(models.TextChoices):
        OVERRIDE = 'override', _('Standart Seçenekleri Ez')
        APPEND = 'append', _('Standart Seçeneklere Ekle')

    name = models.CharField(max_length=255)
    display_mode = models.CharField(
        max_length=10,
        choices=DisplayMode.choices,
        default=DisplayMode.APPEND,
        verbose_name=_("Görüntüleme Modu"),
        help_text=_("Seçeneklerin nasıl gösterileceğini belirler.")
    )
    logical_operator = models.CharField(
        max_length=3,
        choices=[("AND", "AND"), ("OR", "OR")]
    )
    trigger_option_1 = models.ForeignKey(
        Option,
        on_delete=models.CASCADE,
        related_name='trigger_option_1'
    )
    trigger_option_2 = models.ForeignKey(
        Option,
        on_delete=models.CASCADE,
        related_name='trigger_option_2'
    )
    target_question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='conditional_options',
        help_text="Bu koşullu seçeneklerin gösterileceği soru."
    )
    applicable_options = models.ManyToManyField(
        Option,
        related_name='applicable_options',
        help_text="Bu koşullu seçenekler sonucunda gösterilecek seçenekler."
    )

    def get_options(self, standard_options=None):
        """
        Seçenekleri görüntüleme moduna göre döndürür.

        Args:
            standard_options (QuerySet): Standart seçenekler.

        Returns:
            QuerySet: Gösterilecek seçenekler.
        """
        if self.display_mode == self.DisplayMode.OVERRIDE:
            return self.applicable_options.all()
        elif standard_options:
            return standard_options.union(self.applicable_options.all())
        return self.applicable_options.all()

    def __str__(self):
        return f"{self.name} (Trigger: {self.trigger_option_1} {self.logical_operator} {self.trigger_option_2})"

    class Meta:
        verbose_name = "09-Koşullu Seçenek"
        verbose_name_plural = "09-Koşullu Seçenekler"

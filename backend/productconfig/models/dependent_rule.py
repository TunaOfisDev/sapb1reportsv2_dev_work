# backend/productconfig/models/dependent_rule.py
import logging
from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import BaseModel

# Logger tanımı
logger = logging.getLogger(__name__)

class DependentRule(BaseModel):
    """
    ETAJER VAR MI? gibi bağımlı soruları yöneten model.
    Bir sorunun cevabına göre diğer soruları gösterip gizler.
    """
    class RuleType(models.TextChoices):
        SHOW_ON_OPTION = 'show_on_option', _('Seçenek Seçilince Göster')
        HIDE_ON_OPTION = 'hide_on_option', _('Seçenek Seçilince Gizle')

    name = models.CharField(
        max_length=255,
        verbose_name=_("Kural Adı")
    )

    rule_type = models.CharField(
        max_length=20,
        choices=RuleType.choices,
        default=RuleType.SHOW_ON_OPTION,
        verbose_name=_("Kural Tipi")
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Aktif Mi?")
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Sıra")
    )

    # İlişkiler
    parent_question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        related_name='parent_rules',
        verbose_name=_("Ana Soru")
    )

    trigger_option = models.ForeignKey(
        'Option',
        on_delete=models.CASCADE,
        related_name='trigger_rules',
        verbose_name=_("Tetikleyici Seçenek")
    )

    dependent_questions = models.ManyToManyField(
        'Question',
        related_name='dependent_rules',
        verbose_name=_("Bağımlı Sorular")
    )

    class Meta:
        verbose_name = _("06-Bağımlı Soru Kuralı")
        verbose_name_plural = _("06-Bağımlı Soru Kuralları")
        ordering = ['order']


    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"



    def evaluate(self, variant) -> bool:
        """
        Kuralın sağlanıp sağlanmadığını kontrol eder.
        """
        logger.debug(f"Kural değerlendirme başladı: {self.name} (Kural ID: {self.id}, Soru ID: {self.parent_question.id})")
        try:
            # Kullanıcı yanıtını al
            answer = variant.text_answers.get(str(self.parent_question.id))
            if not answer:
                logger.warning(f"Kural değerlendirme başarısız: Yanıt bulunamadı (Soru ID: {self.parent_question.id})")
                return False

            answer_id = answer.get('answer_id')
            if not answer_id:
                logger.warning(f"Kural değerlendirme başarısız: Yanıt ID eksik (Soru ID: {self.parent_question.id})")
                return False

            logger.debug(f"Karşılaştırma yapılacak: Cevap ID {answer_id}, Tetikleyici Seçenek ID {self.trigger_option.id}")

            # Kural Tipine Göre Değerlendirme
            if self.rule_type == self.RuleType.SHOW_ON_OPTION:
                # Seçenek seçildiğinde göster
                result = answer_id == self.trigger_option.id
                logger.info(f"Kural tipi: GÖSTER (SHOW_ON_OPTION). Değerlendirme Sonucu: {result}")
                return result
            elif self.rule_type == self.RuleType.HIDE_ON_OPTION:
                # Seçenek seçildiğinde gizle (mantık tersine çevrildi)
                result = answer_id != self.trigger_option.id
                logger.info(f"Kural tipi: GİZLE (HIDE_ON_OPTION). Değerlendirme Sonucu: {result}")
                return result

            # Beklenmeyen kural türü
            logger.error(f"Geçersiz kural türü: {self.rule_type}")
            return False

        except Exception as e:
            logger.error(f"Kural değerlendirme sırasında hata: {str(e)} (Kural ID: {self.id}, Soru ID: {self.parent_question.id})")
            return False



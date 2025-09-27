# backend/productconfig/models/question_option_relation.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import BaseModel

class QuestionOptionRelation(BaseModel):
    class RelationType(models.TextChoices):
        MASTER = 'master', _('Master')
        MODEL = 'model', _('Model')
        CONDITIONAL = 'conditional', _('Koşullu')

    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        related_name='question_option_relations',
        verbose_name=_("Soru")
    )
    options = models.ManyToManyField(
        'Option',
        related_name='question_option_relations',
        verbose_name=_("Seçenekler")
    )
    relation_type = models.CharField(
        max_length=20,
        choices=RelationType.choices,
        default=RelationType.MASTER,
        verbose_name=_("İlişki Tipi")
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Sıra")
    )

    class Meta:
        verbose_name = _("10-Soru-Seçenek İlişkisi")
        verbose_name_plural = _("10-Soru-Seçenek İlişkileri")
        ordering = ['order']


    def __str__(self):
        return f"{self.question.name} - {self.get_relation_type_display()}"
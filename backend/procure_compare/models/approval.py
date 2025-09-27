# File: backend/procure_compare/models/approval.py

from django.db import models
from django.conf import settings


class PurchaseApproval(models.Model):
    ONAY_DURUM_CHOICES = [
        ('onay', 'Onay'),
        ('kismi_onay', 'Kısmi Onay'),
        ('red', 'Red'),
        ('onay_iptal', 'Onay İptal')
    ]

    belge_no = models.CharField(max_length=20)
    uniq_detail_no = models.CharField(max_length=50)
    action = models.CharField(max_length=20, choices=ONAY_DURUM_CHOICES)
    aciklama = models.TextField(blank=True, null=True)
    satir_detay_json = models.JSONField(null=True, blank=True)

    kullanici = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_approvals'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "purchase_approvals"
        verbose_name = "Purchase Approval"
        verbose_name_plural = "Purchase Approvals"
        # ❌ Bu constraint kaldırıldı çünkü artık sistem onayları iptale göre yönetecek
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['belge_no', 'uniq_detail_no'],
        #         condition=models.Q(action__in=['onay', 'kismi_onay', 'red']),
        #         name='unique_onay_kayitlari_per_line'
        #     ),
        #     models.UniqueConstraint(
        #         fields=['belge_no', 'uniq_detail_no', 'action'],
        #         condition=models.Q(action='onay_iptal'),
        #         name='unique_onay_iptal_per_line'
        #     ),
        # ]

    def __str__(self):
        return f"{self.belge_no} - {self.uniq_detail_no} ({self.get_action_display()})"

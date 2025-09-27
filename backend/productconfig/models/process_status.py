# backend/productconfig/models/process_status.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import BaseModel
from .product_model import ProductModel

class ProcessStatus(BaseModel):
    """
    Ürün modellerinin ilişki durumlarını takip eden model
    """
    product_model = models.OneToOneField(
        ProductModel,
        on_delete=models.CASCADE,
        related_name='process_status',
        verbose_name=_("Ürün Modeli")
    )

    # Mevcut alanlar...
    has_brand_relations = models.BooleanField(
        default=False,
        verbose_name=_("Marka İlişkileri")
    )
    has_group_relations = models.BooleanField(
        default=False,
        verbose_name=_("Grup İlişkileri")
    )
    has_category_relations = models.BooleanField(
        default=False,
        verbose_name=_("Kategori İlişkileri")
    )
    has_question_relations = models.BooleanField(
        default=False,
        verbose_name=_("Soru İlişkileri")
    )
    has_option_relations = models.BooleanField(
        default=False,
        verbose_name=_("Seçenek İlişkileri")
    )

    total_questions = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Toplam Soru Sayısı")
    )
    total_options = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Toplam Seçenek Sayısı")
    )
    
    # Yeni eklenen ölçü seçenek sayısı alanı
    total_dimension_options = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Toplam Seçenek Ölçü Sayısı"),
        help_text=_("Belirlenen gruplardaki CM içeren seçenek sayısı")
    )

    last_check = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Son Kontrol")
    )

    completion_percentage = models.FloatField(
        default=0,
        verbose_name=_("Tamamlanma Yüzdesi")
    )

    class Meta:
        verbose_name = _("İşlem Durumu")
        verbose_name_plural = _("İşlem Durumları")

    def calculate_completion(self):
        """
        Tamamlanma yüzdesini hesaplar
        """
        total_checks = 5
        completed = sum([
            self.has_brand_relations,
            self.has_group_relations,
            self.has_category_relations,
            self.has_question_relations,
            self.has_option_relations
        ])
        
        self.completion_percentage = (completed / total_checks) * 100
        return self.completion_percentage

    def update_status(self):
        """
        Tüm durumları günceller
        """
        product_model = self.product_model

        # Mevcut durum güncellemeleri...
        self.has_brand_relations = product_model.applicable_options.filter(
            applicable_brands__isnull=False
        ).exists()

        self.has_group_relations = product_model.applicable_options.filter(
            applicable_groups__isnull=False
        ).exists()

        self.has_category_relations = product_model.applicable_options.filter(
            applicable_categories__isnull=False
        ).exists()

        self.has_question_relations = product_model.applicable_questions.exists()
        self.has_option_relations = product_model.applicable_options.exists()

        self.total_questions = product_model.applicable_questions.count()
        self.total_options = product_model.applicable_options.count()

        # Ölçü seçenek sayısını hesapla
        self.total_dimension_options = product_model.applicable_options.filter(
            applicable_groups__id__in=[1, 2, 4],  # Belirtilen grup ID'leri
            name__icontains='CM'  # CM içeren seçenekler
        ).distinct().count()

        # Tamamlanma yüzdesini hesapla
        self.calculate_completion()

        self.save()
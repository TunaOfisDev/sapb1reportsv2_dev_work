# backend/productconfig/models/option.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import os
from uuid import uuid4
from .base import BaseModel
from .brand import Brand
from .product_group import ProductGroup
from .category import Category
from .product_model import ProductModel

def option_image_path(instance, filename):
    """
    Yüklenen resim dosyaları için güvenli ve benzersiz bir dosya yolu oluşturur.
    
    Args:
        instance: Option model instance'ı
        filename: Yüklenen dosyanın orijinal adı
    
    Returns:
        str: Oluşturulan dosya yolu
    """
    file_extension = os.path.splitext(filename)[1]
    filename_without_extension = os.path.splitext(filename)[0]
    safe_filename = slugify(filename_without_extension)
    unique_filename = f"{safe_filename}-{str(uuid4())[:8]}{file_extension}"
    return os.path.join('options', unique_filename)

class Option(BaseModel):
    """
    Seçenek modeli, sorulara bağlı seçenekleri temsil eder.
    Her seçenek bir veya birden fazla soruya bağlı olabilir ve
    belirli markalara, gruplara, kategorilere ve ürün modellerine uygulanabilir.
    """
    
    COLOR_CHOICES = (
        ('colored', _('Renkli Ürün')),
        ('colorless', _('Renksiz Ürün')),
        ('both', _('Her İkisi İçin Uygun')),
    )

    OPTION_TYPE_CHOICES = (
        ('model_question_options', _('Model Soru Seçenekleri')),
        ('master_question_options', _('Master Soru Seçenekleri')),
        ('conditional_question_options', _('Koşullu Soru Seçenekleri')),
    )

    # Temel alanlar
    name = models.CharField(
        max_length=255, 
        verbose_name=_("Seçenek Adı")
    )
    
    option_type = models.CharField(
        max_length=30, 
        choices=OPTION_TYPE_CHOICES,
        default='model_question_options',
        verbose_name=_("Seçenek Tipi")
    )

    # Fiyat alanları
    price_modifier = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Fiyat"),
        help_text=_("Seçenek için aktif fiyat. Otomatik olarak güncellenir.")
    )

    normal_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Normal Fiyat"),
        help_text=_("Malzemeye bağımlı olmayan temel fiyat")
    )

    price_melamine = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Melamin Fiyatı")
    )

    price_laminate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Laminat Fiyatı")
    )

    price_veneer = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Kaplama Fiyatı")
    )

    price_lacquer = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Lake Fiyatı")
    )

    color_status = models.CharField(
        max_length=10,
        choices=COLOR_CHOICES,
        default='both',
        verbose_name=_("Renk Durumu")
    )

    variant_code_part = models.CharField(
        max_length=50,
        verbose_name=_("Varyant Kodu Parçası"),
        blank=True,
        null=True,
        help_text=_("Seçenek seçildiğinde varyant koduna eklenecek parça")
    )

    variant_description_part = models.CharField(
        max_length=255,
        verbose_name=_("Varyant Tanımı Parçası"),
        blank=True,
        null=True,
        help_text=_("Seçenek seçildiğinde varyant açıklamasına eklenecek parça")
    )

    image = models.ImageField(
        upload_to=option_image_path,
        null=True,
        blank=True,
        verbose_name=_("Seçenek Resmi"),
        help_text=_("Maksimum dosya boyutu: 5MB. İzin verilen formatlar: JPG, PNG")
    )

    is_popular = models.BooleanField(
        default=False,
        verbose_name=_("Popüler mi?"),
        help_text=_("Popüler seçenekler listede öncelikli gösterilir")
    )
    question_relation_count = models.IntegerField(
        verbose_name='Soru İlişki Sayısı',
        default=0,
        editable=False
    )

    # Malzeme fiyat tetikleyicileri
    melamine_triggers = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='melamine_price_triggers_for',
        verbose_name=_("Melamin Fiyat Tetikleyicileri"),
        help_text=_("Bu seçeneklerden herhangi biri seçildiğinde melamin fiyatı uygulanır")
    )

    laminate_triggers = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='laminate_price_triggers_for',
        verbose_name=_("Laminat Fiyat Tetikleyicileri"),
        help_text=_("Bu seçeneklerden herhangi biri seçildiğinde laminat fiyatı uygulanır")
    )

    veneer_triggers = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='veneer_price_triggers_for',
        verbose_name=_("Kaplama Fiyat Tetikleyicileri"),
        help_text=_("Bu seçeneklerden herhangi biri seçildiğinde kaplama fiyatı uygulanır")
    )

    lacquer_triggers = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='lacquer_price_triggers_for',
        verbose_name=_("Lake Fiyat Tetikleyicileri"),
        help_text=_("Bu seçeneklerden herhangi biri seçildiğinde lake fiyatı uygulanır")
    )

    # İlişkisel alanlar
    applicable_brands = models.ManyToManyField(
        Brand,
        related_name="applicable_options",
        blank=True,
        verbose_name=_("İlgili Markalar"),
        help_text=_("Bu seçeneğin uygulanabileceği markalar")
    )

    applicable_groups = models.ManyToManyField(
        ProductGroup,
        blank=True,
        related_name="applicable_options",
        verbose_name=_("İlgili Gruplar"),
        help_text=_("Bu seçeneğin uygulanabileceği ürün grupları")
    )

    applicable_categories = models.ManyToManyField(
        Category,
        related_name="applicable_options",
        blank=True,
        verbose_name=_("İlgili Kategoriler"),
        help_text=_("Bu seçeneğin uygulanabileceği kategoriler")
    )

    applicable_product_models = models.ManyToManyField(
        ProductModel,
        related_name="applicable_options",
        blank=True,
        verbose_name=_("İlgili Ürün Modelleri"),
        help_text=_("Bu seçeneğin uygulanabileceği ürün modelleri")
    )

    class Meta:
        verbose_name = _("08-Seçenek")
        verbose_name_plural = _("08-Seçenekler")
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['option_type']),
            models.Index(fields=['is_popular']),
        ]

    def __str__(self):
        return f"{self.name} - {self.get_option_type_display()}{' - ' + self.variant_code_part if self.variant_code_part else ''}"

    def clean(self):
        """Model validasyonu için clean methodu"""
        super().clean()
        if self.image:
            # Dosya boyutu kontrolü (5MB)
            if self.image.size > 5 * 1024 * 1024:
                raise ValidationError(_("Resim dosyası 5MB'dan büyük olamaz."))
            
            # Dosya tipi kontrolü
            valid_extensions = ['.jpg', '.jpeg', '.png']
            ext = os.path.splitext(self.image.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError(_("Sadece JPG ve PNG dosyaları yüklenebilir."))

    def delete(self, *args, **kwargs):
        """Option silindiğinde ilişkili resmi de sil"""
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        """Option kaydedildiğinde fiyat ve resim güncellemelerini yap"""
        # İlk olarak temel nesneyi kaydediyoruz
        super().save(*args, **kwargs)

        # ManyToMany ilişkiler üzerinde işlem yapmadan önce nesnenin bir `id`si olduğundan emin olunmalı.
        if self.pk:
            from .variant import Variant  # Circular import'u önlemek için local import
            variants_with_this_option = Variant.objects.filter(options=self)
            
            for variant in variants_with_this_option:
                selected_option_ids = set()
                for answer in variant.text_answers.values():
                    if 'answer_id' in answer:
                        selected_option_ids.add(answer['answer_id'])
                    elif 'answer_ids' in answer:
                        selected_option_ids.update(answer['answer_ids'])

                # Tetikleyicilere göre fiyat belirleme
                if any(trigger.id in selected_option_ids for trigger in self.melamine_triggers.all()):
                    self.price_modifier = self.price_melamine
                elif any(trigger.id in selected_option_ids for trigger in self.laminate_triggers.all()):
                    self.price_modifier = self.price_laminate
                elif any(trigger.id in selected_option_ids for trigger in self.veneer_triggers.all()):
                    self.price_modifier = self.price_veneer
                elif any(trigger.id in selected_option_ids for trigger in self.lacquer_triggers.all()):
                    self.price_modifier = self.price_lacquer
                else:
                    self.price_modifier = self.normal_price

            # Fiyat güncellemesini kaydedin
            super().save(*args, **kwargs)


    @property
    def get_image_url(self):
        """Resmin URL'sini döndürür. Resim yoksa None döner."""
        if self.image:
            return self.image.url
        return None

    def is_applicable_for_variant(self, variant) -> bool:
        """
        Seçeneğin belirli bir varyant için uygulanabilir olup olmadığını kontrol eder.
        Tüm applicable_* alanlarında en az bir eşleşme olmalıdır.
        """
        # Eğer hiçbir applicable alanı set edilmemişse, her durumda uygulanabilir
        if not (self.applicable_brands.exists() or 
                self.applicable_groups.exists() or 
                self.applicable_categories.exists() or 
                self.applicable_product_models.exists()):
            return True

        # Brand kontrolü
        if self.applicable_brands.exists():
            if not variant.brand or variant.brand not in self.applicable_brands.all():
                return False

        # Group kontrolü
        if self.applicable_groups.exists():
            if not variant.product_group or variant.product_group not in self.applicable_groups.all():
                return False

        # Category kontrolü
        if self.applicable_categories.exists():
            if not variant.category or variant.category not in self.applicable_categories.all():
                return False

        # Product Model kontrolü
        if self.applicable_product_models.exists():
            if not variant.product_model or variant.product_model not in self.applicable_product_models.all():
                return False

        return True
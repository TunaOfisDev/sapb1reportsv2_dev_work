# backend/productconfig_simulator/models/simulated_variant.py
from django.db import models
from django.utils.translation import gettext_lazy as _
# from django.contrib.postgres.fields import JSONField  # Bu satırı kaldırın
from django.db.models import JSONField  # Bunun yerine bunu kullanın

from .base import SimulatorBaseModel
from productconfig.models import ProductModel, Option
from .simulation_job import SimulationJob

class SimulatedVariant(SimulatorBaseModel):
    """
    Simülasyon sırasında oluşturulan varyantları temsil eden model.
    """
    simulation = models.ForeignKey(
        SimulationJob,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name=_("Simülasyon")
    )
    
    product_model = models.ForeignKey(
        ProductModel,
        on_delete=models.CASCADE,
        related_name='simulated_variants',
        verbose_name=_("Ürün Modeli")
    )
    
    variant_code = models.CharField(
        max_length=255,
        verbose_name=_("Varyant Kodu")
    )
    
    variant_description = models.TextField(
        blank=True,
        verbose_name=_("Varyant Tanımı")
    )
    
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Toplam Fiyat")
    )
    
    text_answers = JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Metin Cevaplar")
    )
    
    selected_options = models.ManyToManyField(
        Option,
        related_name='simulated_variants',
        blank=True,
        verbose_name=_("Seçilen Seçenekler")
    )
    
    old_component_codes = JSONField(
        default=list,
        blank=True,
        verbose_name=_("Eski Bileşen Kodları")
    )
    
    class Meta:
        verbose_name = _("Simüle Edilmiş Varyant")
        verbose_name_plural = _("Simüle Edilmiş Varyantlar")
        ordering = ['product_model', 'variant_code']
        indexes = [
            models.Index(fields=['simulation', 'product_model']),
            models.Index(fields=['variant_code']),
        ]
    
    def __str__(self):
        return f"{self.product_model.name} - {self.variant_code}"
    
    def to_dict(self):
        """Bu varyantı sözlük formatına dönüştürür (API ve raporlama için)"""
        return {
            'id': self.id,
            'product_model': {
                'id': self.product_model.id,
                'name': self.product_model.name,
            },
            'variant_code': self.variant_code,
            'variant_description': self.variant_description,
            'total_price': float(self.total_price),
            'text_answers': self.text_answers,
            'old_component_codes': self.old_component_codes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def compare_with_actual(self, actual_variant=None):
        """
        Bu simüle edilmiş varyantı, gerçek varyant ile karşılaştırır.
        Eğer actual_variant belirtilmezse, veritabanından variant_code ile eşleşen kaydı arar.
        
        Returns:
            dict: Karşılaştırma sonuçlarını içeren sözlük
        """
        from backend.productconfig.models import Variant
        
        if not actual_variant:
            try:
                actual_variant = Variant.objects.get(variant_code=self.variant_code)
            except Variant.DoesNotExist:
                return {'exists': False, 'message': 'Gerçek varyant bulunamadı'}
        
        # Karşılaştırma sonuçları
        comparison = {
            'exists': True,
            'price_match': abs(float(self.total_price) - float(actual_variant.total_price)) < 0.01,
            'description_match': self.variant_description == actual_variant.variant_description,
            'options_count_match': (
                self.selected_options.count() == actual_variant.options.count()
            ),
        }
        
        # Farklılıkları hesapla
        if not comparison['price_match']:
            comparison['price_diff'] = {
                'simulated': float(self.total_price),
                'actual': float(actual_variant.total_price),
            }
        
        if not comparison['description_match']:
            comparison['description_diff'] = {
                'simulated': self.variant_description,
                'actual': actual_variant.variant_description,
            }
        
        return comparison
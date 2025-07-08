# backend/productconfig/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ProductModel, ProcessStatus

@receiver(post_save, sender=ProductModel)
def create_or_update_process_status(sender, instance, created, **kwargs):
    """
    ProductModel kaydedildiğinde ProcessStatus'u oluştur veya güncelle
    """
    process_status, _ = ProcessStatus.objects.get_or_create(product_model=instance)
    process_status.update_status()

@receiver(post_delete, sender=ProductModel)
def delete_process_status(sender, instance, **kwargs):
    """
    ProductModel silindiğinde ProcessStatus'u da sil
    """
    ProcessStatus.objects.filter(product_model=instance).delete()


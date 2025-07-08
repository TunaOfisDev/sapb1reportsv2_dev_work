# backend/productconfig/services/base_service.py
from django.core.exceptions import ObjectDoesNotExist
from ..utils.base_helper import BaseHelper

class BaseService:
    """
    Tüm servis sınıfları için temel işlevselliği sağlayan BaseService sınıfı.
    Servis sınıflarında sıkça kullanılan işlemleri içerir.
    """
   
    def __init__(self):
        self.helper = BaseHelper() 

    def get_instance(self, model, id):
        """
        Belirli bir modelden ID ile bir nesne getirir.
        """
        instance = self.helper.get_by_id(model, id)
        if not instance:
            raise ObjectDoesNotExist(f"{model.__name__} with ID {id} not found.")
        return instance

    def create_instance(self, model, data):
        """
        Verilen modelde yeni bir nesne oluşturur.
        """
        instance = model.objects.create(**data)
        return instance

    def update_instance(self, instance, data):
        """
        Var olan bir nesneyi günceller ve kaydeder.
        """
        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def delete_instance(self, instance, soft_delete=True):
        """
        Bir nesneyi siler. Soft delete yapılırsa, is_active alanı False olur.
        """
        if soft_delete:
            instance.delete()
        else:
            instance.hard_delete()

    def restore_instance(self, instance):
        """
        Silinmiş bir nesneyi geri getirir (restore).
        """
        instance.restore()

    
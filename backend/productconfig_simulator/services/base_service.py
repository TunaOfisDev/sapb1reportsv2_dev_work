# backend/productconfig_simulator/services/base_service.py
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet, Model

class BaseService:
    """
    Tüm servis sınıfları için temel işlevselliği sağlayan BaseService sınıfı.
    """
   
    def __init__(self, model_class=None):
        self.model_class = model_class
    
    def get_all(self) -> QuerySet:
        """
        Modele ait tüm aktif kayıtları döndürür.
        """
        if not self.model_class:
            raise ValueError("Model sınıfı belirtilmemiş")
        return self.model_class.objects.filter(is_active=True)

    def get_by_id(self, id: int):
        """
        Belirtilen ID'ye sahip modeli döndürür.
        """
        if not self.model_class:
            raise ValueError("Model sınıfı belirtilmemiş")
            
        try:
            return self.model_class.objects.get(id=id, is_active=True)
        except self.model_class.DoesNotExist:
            raise ObjectDoesNotExist(f"{self.model_class.__name__} with ID {id} not found.")

    def create(self, **data):
        """
        Yeni bir kayıt oluşturur ve döndürür.
        """
        if not self.model_class:
            raise ValueError("Model sınıfı belirtilmemiş")
            
        instance = self.model_class(**data)
        instance.save()
        return instance
    
    def update(self, instance, **data):
        """
        Var olan bir kaydı günceller.
        """
        if not isinstance(instance, Model):
            raise ValueError("Instance bir model nesnesi olmalıdır")
            
        for key, value in data.items():
            setattr(instance, key, value)
        
        instance.save()
        return instance
    
    def delete(self, instance, hard_delete=False):
        """
        Bir kaydı siler. Varsayılan olarak soft delete yapar.
        """
        if not isinstance(instance, Model):
            raise ValueError("Instance bir model nesnesi olmalıdır")
            
        if hard_delete:
            instance.hard_delete()
        else:
            instance.delete()
    
    def filter_by(self, **kwargs) -> QuerySet:
        """
        Belirtilen kriterlere göre filtrelenmiş kayıtları döndürür.
        """
        if not self.model_class:
            raise ValueError("Model sınıfı belirtilmemiş")
            
        # Özel is_active filtresi ekle, aksi belirtilmedikçe
        if 'is_active' not in kwargs:
            kwargs['is_active'] = True
            
        return self.model_class.objects.filter(**kwargs)
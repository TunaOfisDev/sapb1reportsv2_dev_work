# backend/productconfig/utils/base_helper.py

class BaseHelper:
    """
    Tüm helper sınıfları için temel işlevselliği sağlayan BaseHelper sınıfı.
    Ortak işlemler bu sınıfta tanımlanır ve diğer helper sınıfları tarafından miras alınır.
    """

    def activate(self, instance):
        """
        Verilen bir nesneyi aktifleştirir.
        """
        instance.is_active = True
        instance.save()
        return instance

    def deactivate(self, instance):
        """
        Verilen bir nesneyi pasifleştirir.
        """
        instance.is_active = False
        instance.save()
        return instance

    def get_by_id(self, model, id):
        """
        Verilen modelden belirli bir ID'ye sahip aktif kaydı getirir.
        """
        return model.objects.filter(id=id, is_active=True).first()

    def get_all(self, model):
        """
        Verilen modeldeki tüm aktif kayıtları getirir.
        """
        return model.objects.filter(is_active=True)

    def filter_by_params(self, model, **params):
        """
        Verilen modelde belirli parametrelere göre aktif kayıtları filtreler.
        """
        params['is_active'] = True
        return model.objects.filter(**params)

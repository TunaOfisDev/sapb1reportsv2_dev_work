# backend/newcustomerform/api/serializers.py
from rest_framework import serializers
from newcustomerform.models.models import NewCustomerForm, AuthorizedPerson
import logging

logger = logging.getLogger(__name__)

class AuthorizedPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorizedPerson
        fields = ['ad_soyad', 'telefon', 'email']
        extra_kwargs = {
            'ad_soyad': {'required': False},
            'telefon': {'required': False},
            'email': {'required': False},
        }

class NewCustomerFormSerializer(serializers.ModelSerializer):
    yetkili_kisiler = AuthorizedPersonSerializer(many=True, required=False)

    class Meta:
        model = NewCustomerForm
        fields = [
            'id',
            'firma_unvani',
            'vergi_kimlik_numarasi',
            'vergi_dairesi',
            'firma_adresi',
            'telefon_numarasi',
            'email',
            'muhasebe_irtibat_telefon',
            'muhasebe_irtibat_email',
            'odeme_sartlari',
            'iskonto_anlasmasi',
            'vergi_levhasi',  # Modelde tanımlı olan alan adı
            'faaliyet_belgesi',
            'ticaret_sicil',
            'imza_sirkuleri',
            'banka_iban',
            'yetkili_kisiler',
            'created_by',
            'created_at'
        ]

    def create(self, validated_data, **kwargs):
        """
        Yeni müşteri formu ve yetkili kişileri oluşturur.
        Ekstra olarak gelen created_by bilgisini validated_data'dan çıkarıp, 
        model oluşturma işlemine dahil etmez.
        """
        # Ekstra gelen created_by bilgisini validated_data'dan çıkarıyoruz.
        created_by = validated_data.pop('created_by', None)
        
        # Yetkili kişiler verisini çıkar
        yetkili_kisiler_data = validated_data.pop('yetkili_kisiler', [])
        
        # Sadece modelde tanımlı alanları kullanarak formu oluştur
        new_customer_form = NewCustomerForm.objects.create(**validated_data)
        
        # Eğer istersen, burada created_by bilgisini başka bir işlemde kullanabilirsin.
        # Örneğin; mail servisine gönderirken ya da loglamada.
        
        # Yetkili kişileri ekle
        for yetkili_data in yetkili_kisiler_data:
            # İlgili alanların kontrolünü yaparak yetkili kişiyi oluşturuyoruz.
            if not all(key in yetkili_data for key in ['ad_soyad', 'telefon', 'email']):
                raise serializers.ValidationError({
                    'yetkili_kisiler': 'Her yetkili kişi için ad_soyad, telefon ve email alanları zorunludur.'
                })
            AuthorizedPerson.objects.create(new_customer_form=new_customer_form, **yetkili_data)
        
        return new_customer_form


    def update(self, instance, validated_data):
        """
        Müşteri formunu güncelle ve yetkili kişileri güncelle.
        """
        yetkili_kisiler_data = validated_data.pop('yetkili_kisiler', [])
        instance = super().update(instance, validated_data)

        # **Yetkili Kişileri Güncelle**
        instance.yetkili_kisiler.all().delete()  # ✅ Önceki yetkili kişileri temizle
        for yetkili_data in yetkili_kisiler_data:
            AuthorizedPerson.objects.create(new_customer_form=instance, **yetkili_data)

        return instance

    def to_representation(self, instance):
        """
        API'den GET isteği yapıldığında yetkili kişileri JSON formatında döndür.
        """
        rep = super().to_representation(instance)
        rep['yetkili_kisiler'] = AuthorizedPersonSerializer(instance.yetkili_kisiler.all(), many=True).data
        return rep

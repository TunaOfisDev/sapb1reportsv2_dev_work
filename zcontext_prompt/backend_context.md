# backend/backend_context.md
### ✅ **Güncellenmiş `zcontext_prompt/backend_context.md` v3.0**

```markdown
# ============================================================================
# CONTEXT-1: SAPB1ReportsV2 Backend Anayasası v3.0
# ============================================================================
# BU BELGE, YENİ BİR DJANGO UYGULAMASI ÜRETMEK İÇİN KESİN VE TAVİZSİZ
# KURALLARI İÇERİR. AI, BU KURALLARI BİR ANAYASA OLARAK KABUL ETMEK ZORUNDADIR.
# ============================================================================

## 1. 🎯 Amaç
Bu belgenin tek amacı, `sapb1reportsv2` projesine eklenecek her yeni Django uygulamasının (`<module_name>`), projenin mevcut yapısıyla %100 uyumlu, "tak-çalıştır" (plug-and-play) şeklinde, hatasız ve standartlara uygun olarak üretilmesini sağlamaktır. AI, bu belgedeki kuralları ASLA esnetemez veya yorumlayamaz.

---

## 2. 📁 Zorunlu Klasör ve Dosya Yapısı
Yeni bir `<module_name>` uygulaması, `backend/` dizini altında aşağıdaki hiyerarşiye sahip olmak **ZORUNDADIR**:

```

backend/\<module\_name\>/
├── **init**.py
├── admin.py
├── apps.py
├── api/
│   ├── **init**.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── migrations/
│   └── **init**.py
├── models/
│   ├── **init**.py
│   └── \<module\_name\>.py
├── services/
│   ├── **init**.py
│   └── \<module\_name\>\_service.py
├── tasks/
│   ├── **init**.py
│   └── \<module\_name\>*tasks.py
└── tests/
├── **init**.py
└── test*\<module\_name\>.py

````

---

## 3. 📜 Kodlama ve Mimari Kuralları
| Kural | Açıklama |
| --- | --- |
| **Dosya Yolu Yorumu**| Her `.py` dosyası, `# path: backend/<path>/dosya_adi.py` formatında bir yorumla başlamalıdır. |
| **İsimlendirme** | Dosyalar `snake_case`, Sınıflar `CamelCase` olmalıdır. |
| **Model Alanları** | Tüm model alanları, admin panelinde okunabilirlik için Türkçe `verbose_name` içermelidir. |
| **Mimari Katmanlar** | **View -> Service -> Model.** `views.py` ASLA doğrudan veritabanına erişmez. Her zaman `services` katmanını çağırır. |
| **Logging** | Proje genelinde `loguru` kullanılır. Ayarlar `sapreports/logger_settings.py` dosyasındadır. |
| **Tip İpuçları** | Tüm fonksiyon ve metodlarda *PEP 484* standartlarına uygun tip ipuçları kullanılmalıdır. |

> **KRİTİK MİMARİ KURAL DETAYI:**
> "View -> Service -> Model" kuralının en önemli uygulama alanı `views.py` dosyasıdır.
> - **`queryset` sınıf değişkeni ASLA kullanılmamalıdır (`queryset = Model.objects.all()` KESİNLİKLE YASAKTIR!).**
> - Bunun yerine, daima `get_queryset(self)` metodu override edilmeli ve bu metot, veriyi çekmek için **servis katmanındaki** bir fonksiyonu çağırmalıdır.

---

## 4. 🔗 Proje Entegrasyonu (`README.md` İçin Talimatlar)
(Bu bölüm değişmedi.)
1.  **`INSTALLED_APPS`:** `'<module_name>.apps.<ModuleName>Config'` satırını `backend/sapreports/settings.py`'e ekle.
2.  **`urls.py`:** `path('api/v1/<module_name>/', include('<module_name>.api.urls'))` satırını ana `urls.py`'a ekle.
3.  **`celery.py`:** Eğer görev varsa, `"<module_name>.tasks"` satırını `CELERY_IMPORTS` listesine ekle.

---

## 5. 🤝 API Sözleşmesi
(Bu bölüm değişmedi.)
| Başlık | Standart |
| --- | --- |
| **Authentication** | `rest_framework_simplejwt.authentication.JWTAuthentication`. Header: `Authorization: Bearer <token>` |
| **Response Şablonu** | Tüm yanıtlar standart JSON yapısında olmalıdır: `{"success": bool, "data": {}, "message": str, "errors": {}}`. **Başarısız yanıtlarda `errors` alanı dolu olmalıdır.** |
| **Hata Mesajları** | Kullanıcıya dönen hata mesajları genel olmalıdır ("Bir hata oluştu."). Detaylı teknik hata `loguru` ile loglanmalıdır. |

---

## 6. 🏆 En İyi Pratikler ve "Altın Standart" Kod Örnekleri

#### 6.1. Serializer Örneği (Güvenlik Odaklı)
`fields = '__all__'` kullanımı **KESİNLİKLE YASAKTIR**.
```python
# path: backend/<module_name>/api/serializers.py
from rest_framework import serializers
from ..models import <YourModel>, <RelatedModel>
from django.contrib.auth.models import User

class <YourModel>Serializer(serializers.ModelSerializer):
    # İlişkili modelden sadece istenen bir alanı okumak için
    related_model_name = serializers.CharField(source='related_model.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = <YourModel>
        # Alanlar HER ZAMAN açıkça listelenmelidir.
        fields = [
            'id',
            'name',
            'is_active',
            'related_model', # Yazma işlemleri için ID kullanılır
            'related_model_name', # Okuma işlemleri için isim gösterilir
            'created_by_username',
            'created_at',
        ]
        # Otomatik (hem DB hem uygulama seviyesinde) oluşturulan alanlar sadece okunabilir olmalıdır.
        read_only_fields = ['created_at', 'created_by_username']
        
        # DİKKAT: View katmanında perform_create gibi bir metotla otomatik atanan alanlar
        # (örneğin 'created_by') de güvenlik ve veri bütünlüğü için `fields` listesinde
        # yer almamalı, bunun yerine yukarıdaki gibi `source` kullanılarak okunmalıdır.
````

#### 6.2. Servis Fonksiyonu Örneği (Defansif Programlama)

```python
# path: backend/<module_name>/services/<module_name>_service.py
from ..models import <YourModel>
from django.core.exceptions import ValidationError
from typing import Iterable

# LİSTELEME (READ) FONKSİYONLARI İÇİN ÖRNEK
def get_all_records() -> Iterable[<YourModel>]:
    """Tüm <YourModel> kayıtlarını döndürür."""
    return <YourModel>.objects.all()

# FİLTRELİ LİSTELEME (READ) FONKSİYONLARI İÇİN ÖRNEK
def get_records_by_status(status: str | None) -> Iterable[<YourModel>]:
    """Duruma göre <YourModel> kayıtlarını döndürür."""
    # Eğer parametre gelmezse, veri sızıntısını önlemek için ASLA tüm kayıtları dönme.
    if not status:
        return <YourModel>.objects.none()

    if status not in ['active', 'passive']:
        raise ValidationError("Geçersiz status değeri.")

    return <YourModel>.objects.filter(status=status)
```

#### 6.3. ViewSet Örneği

```python
# path: backend/<module_name>/api/views.py
from rest_framework import viewsets
from ..services import <module_name>_service as service

class <ModuleName>ViewSet(viewsets.ModelViewSet):
    serializer_class = <ModuleName>Serializer
    
    # DİKKAT: 'queryset = Model.objects.all()' ASLA kullanılmaz.
    # Veri çekme işlemleri her zaman get_queryset içinden service çağırarak yapılır.
    def get_queryset(self):
        # ViewSet, filtreleme mantığını bilmez, sadece servisi çağırır.
        status = self.request.query_params.get('status')
        if status:
            return service.get_records_by_status(status=status)
        return service.get_all_records()

    # Özel iş mantığı (örneğin request.user ataması) perform_* metotlarına yazılır.
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
```

##### 6.3.1. Temel Metotları Değiştirmeme Kuralı

`ModelViewSet`'in `create`, `update`, `list` gibi temel metotlarını, özel bir neden olmadıkça **ASLA override etme.** Django REST Framework bu metotları standart iş akışları (validasyon, `perform_*` çağırma, yanıt oluşturma) için tasarlamıştır. Bunları override etmek, kod tekrarına ve hatalara yol açar. Özel iş mantığını **HER ZAMAN** `perform_create(self, serializer)` veya `perform_update(self, serializer)` gibi `perform_*` metotlarının içine yaz.

#### 6.4. Admin Paneli Örneği (`admin.py`)

(Bu bölüm değişmedi.)

```python
# path: backend/<module_name>/admin.py
from django.contrib import admin
from .models import <YourModel>

@admin.register(<YourModel>)
class <YourModelAdmin>(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    # Otomatik oluşturulan veya hassas alanların düzenlenmesini engelle
    readonly_fields = ('created_at', 'updated_at')
```
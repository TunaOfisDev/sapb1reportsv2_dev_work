**HANADBCON API Dokümantasyonu**

**. API'nin Genel Amaç ve İşlevselliği:**
   - **Amaç**: HANADBCON API, HANA veritabanından ham veriyi çekmek ve bu veriyi alt servislere iletmek için oluşturulmuştur.
   - **İşlevselliği**: API, veriyi işlemeden ve formatlamadan doğrudan sağlar, bu sayede alt servislerin veriyi kendi ihtiyaçlarına göre işlemesine olanak tanır.


. **Veri Modeli Oluşturma**:
   - `SQLQuery` adında bir model oluşturun. Bu model, `query_name`, `sql_query`, `parameters` (JSON formatında), ve `description` alanlarını içermelidir.

. **HANA DB Bağlantısı**:
   - HANA DB'ye bağlanmak için gerekli ayarları (`host`, `port`, `user`, `password`, `database`) içeren bir yapı kurun.

. **SQL Sorgusu Çalıştırma**:
   - Kullanıcıdan gelen `query_name` ile `SQLQuery` modelindeki ilgili sorguyu bulun.
   - Eğer sorguda `parameters` varsa, bu parametreleri sorguya ekleyin.
   - Sorguyu HANA DB'de çalıştırın ve sonuçları alın.

**. Veri İşleme ve İletim:**
   - **Ham Veri İletimi**: HANADBCON, gelen sorgu sonuçlarını alt servislere iletirken herhangi bir formatlama yapmaz. Ham veriyi eksiksiz bir şekilde iletmeyi hedefler.
   - **Alt Servis İşlemi**: Alt servisler, kendi tanımladıkları formatlama kurallarına göre veriyi işler ve kullanır.


**. Model Tanımında Format Bilgisi:**
   - Her alt servis, veri modelini tanımlarken bu model için gereken format bilgisini de tanımlar.
   - Formatlama bilgisi, tarih formatı, sayısal değerlerin biçimi, metin uzunluğu gibi detayları içerir.
**. Veri Formatlama Yaklaşımı:**
   - **Özelleştirilebilir Formatlama**: Veri formatlama, her alt servisin kendi veri modelini tanımlarken belirlediği özelleştirilebilir formata göre yapılır.
   - **Veri İşleme Esnekliği**: HANADBCON'dan gelen ham veri, her servisin özel ihtiyaçlarına göre işlenebilir.


   Model Dosyaları:
        backend/hanadbcon/models/base.py: Temel model sınıflarını içerir.
        backend/hanadbcon/models/sq_query_model.py: SQLQuery modelini tanımlar. Bu model, SQL sorgularını, parametrelerini ve ilgili açıklamaları içerir.

    Veritabanı Bağlantı Ayarları:
        backend/hanadbcon/utilities/hanadb_config.py: HANA DB'ye bağlanmak için gerekli ayarları içerir. Bu dosya, veritabanı bağlantı bilgilerini ve bağlantıyı oluşturacak fonksiyonları içermelidir.

    API Yapılandırması:
        backend/hanadbcon/api/urls.py: API'nin URL yapılandırmalarını içerir.
        backend/hanadbcon/api/views.py: API'nin view fonksiyonlarını içerir. Bu view'lar, gelen isteklere göre ilgili SQL sorgularını çalıştırır ve sonuçları döndürür.

    Dokümantasyon:
        backend/hanadbcon/docs/hanadbcon_api.md: API'nin genel amaç ve işlevselliğini, veri modelini, veri işleme ve iletim yaklaşımlarını açıklayan dökümantasyondur.

    Django Yapılandırma Dosyaları:
        backend/hanadbcon/__init__.py: Python'un bu dizini bir paket olarak tanıması için gereklidir.
        backend/hanadbcon/admin.py: Django admin paneli için yapılandırmaları içerir.
        backend/hanadbcon/apps.py: Uygulamanın Django'daki yapılandırmasını içerir.
        backend/hanadbcon/tests.py: Uygulama için yazılacak testleri içerir.
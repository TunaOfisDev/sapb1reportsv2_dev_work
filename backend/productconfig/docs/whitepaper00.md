### ProductConfig: Modüler Üretim için Akıllı Konfigürasyon Sistemi

---

#### **Giriş**
ProductConfig, özellikle mobilya, makine ve endüstriyel ekipman gibi modüler üretim yapan sektörlerin ürün varyasyon yönetimi sorunlarını çözmek için geliştirilmiş bir konfigürasyon yönetim sistemidir. Sistem, müşteri taleplerine göre özelleştirilebilir ürünlerin oluşturulmasında, doğru konfigürasyonun hızlı bir şekilde yapılmasına ve süreçlerin dijitalleştirilmesine odaklanır.

---

#### **Projenin Amacı**
ProductConfig, karmaşık üretim süreçlerini optimize etmek, maliyetleri azaltmak ve üretim verimliliğini artırmak amacıyla tasarlanmıştır. Öne çıkan hedefler şunlardır:
- **Hızlı ve Doğru Konfigürasyon**: Müşteri taleplerini karşılayan doğru ürün varyantlarının hızlı bir şekilde oluşturulması.
- **Hata Yönetimi**: Yanlış konfigürasyonların önlenmesi ve üretim süreçlerindeki fire oranlarının azaltılması.
- **Entegrasyon**: ERP sistemleri (SAP HANA ve Logo DB) ile entegre çalışarak verilerin doğru ve hızlı aktarımı.
- **Modülerlik ve Esneklik**: Yeni ürün modelleri ve konfigürasyon gereksinimlerine hızlı uyum sağlama.

---

#### **Teknolojiler**
ProductConfig, modern web teknolojileriyle geliştirilmiş bir tam yığın (full-stack) çözümdür:
- **Backend**:
  - **Framework**: Django Rest Framework (DRF)
  - **Veritabanı**: PostgreSQL
  - **Cache ve Mesajlaşma**: Redis
  - **Asenkron Görevler**: Celery
  - **API Yönetimi**: RESTful servisler ve JWT tabanlı kimlik doğrulama
  - **Özelleştirilmiş Modüller**: `productconfig`, `hanadbcon`, `logocustomerbalance`
- **Frontend**:
  - **Framework**: React.js
  - **Durum Yönetimi**: Redux Toolkit
  - **UI Bileşenleri**: Modüler ve yeniden kullanılabilir bileşenler
  - **Styling**: CSS modülleri ve temalar
- **Entegrasyon**:
  - SAP HANA ve Logo DB gibi ERP sistemleriyle entegrasyon.
  - REST API üzerinden veri alışverişi.

---

#### **Servis Katmanı (Service Layer) Mantıkları**
Servis katmanı, uygulamanın iş mantığını ve veri işleme süreçlerini kapsar. Bu katmanda bulunan önemli servisler ve işlevleri aşağıda açıklanmıştır:

##### 1. **BaseService**
Tüm servislerin temel sınıfıdır ve ortak işlevleri içerir:
- **`get_by_id`**: Verilen model ve ID'ye göre kayıt getirir.
- **`delete_by_id`**: Verilen ID'ye göre kayıt siler.

##### 2. **BrandService**
Marka işlemleri için özel servis:
- **`get_all_brands`**: Tüm markaları döndürür.
- **`create_brand`**: Yeni marka oluşturur.
- **`update_brand`**: Mevcut bir markayı günceller.

##### 3. **CategoryService**
Kategorilerle ilgili işlemleri yönetir:
- **`get_all_categories`**: Tüm kategorileri döndürür.
- **`create_category`**: Yeni bir kategori oluşturur.

##### 4. **OptionService**
Ürün seçeneklerini yönetir:
- **`get_all_options`**: Tüm seçenekleri listeler.
- **`calculate_total_price_for_options`**: Seçilen seçeneklerin toplam fiyatını hesaplar.

##### 5. **VariantService**
Ürün varyantlarının oluşturulması ve yönetimi:
- **`create_variant`**: Yeni bir varyant oluşturur.
- **`fetch_variant_details`**: Belirli bir varyantın detaylarını getirir.
- **`update_variant_details`**: Varyant üzerinde yapılan değişiklikleri günceller.

##### 6. **DependentRuleService**
Bağımlı kuralları yönetir:
- **`evaluate_rule`**: Kullanıcı seçimlerine göre kuralların uygunluğunu değerlendirir.

##### 7. **ConditionalOptionsService**
Koşullu seçenekleri işler:
- **`get_conditional_options_by_trigger`**: Belirli bir tetikleyiciye bağlı seçenekleri getirir.

##### 8. **PriceMultiplierService**
Fiyat çarpan kurallarını uygular:
- **`calculate_multiplier`**: Belirli bir seçenek kombinasyonu için fiyat çarpanı hesaplar.

---

#### **Frontend Yapısı ve İşlevselliği**
Frontend katmanı, kullanıcı etkileşimlerini ve konfigürasyon süreçlerini yönetir. Başlıca bileşenler şunlardır:

##### 1. **Common Bileşenler**
- **PCButton**: Farklı stillerde butonlar.
- **PCModal**: Açılır pencere bileşenleri.

##### 2. **Configuration Akışı**
- **PCConfigurationFlow**: Kullanıcıların adım adım ürün konfigürasyonu yapmasını sağlar.
- **PCQuestionCard**: Soruları ve olası cevapları gösterir.
- **PCVariantSummary**: Varyantın özetini görüntüler.

##### 3. **Variant Yönetimi**
- **PCVariantList**: Kullanıcıların tüm varyantlarını listeleyebileceği bir tablo sağlar.
- **PCVariantDetails**: Seçilen varyantın detaylarını gösterir.

##### 4. **Redux Store**
- **pcConfigurationSlice**: Konfigürasyon akışını yönetir.
- **pcVariantSlice**: Varyant durumunu ve listeleme işlemlerini kontrol eder.

---

#### **Sonuç**
ProductConfig, modüler üretim yapan şirketler için bir devrim niteliğinde bir çözümdür. Modern yazılım mimarisi ve güçlü iş mantıkları sayesinde kullanıcılar, karmaşık varyasyon yönetimini kolaylıkla gerçekleştirebilir ve üretim süreçlerinde verimliliği artırabilir.

Bu proje, özelleştirilebilir bir altyapı ile geniş bir kullanıcı kitlesine hitap eder ve gelecekteki geliştirme ihtiyaçlarına hızla adapte olabilecek şekilde tasarlanmıştır. Daha fazla bilgi veya geliştirme önerileri için bu whitepaper bir temel teşkil etmektedir. 

### **Kritik Backend Dosyaları ve Amaçları**

Aşağıda ProductConfig backend projesindeki kritik dosyalar ve amaçları açıklanmıştır:

---

#### 1. **`backend/productconfig/models/variant.py`**
- **Amaç**: Varyant modeli, kullanıcı yapılandırması sonucunda oluşturulan ürün varyantlarını temsil eder.
- **İşlevler**:
  - Varyantın temel bilgilerini (kod, açıklama, fiyat) ve seçilen seçenekleri saklar.
  - Ürün varyantlarının durumunu (taslak, tamamlandı, vb.) takip eder.
  - Varyant bazlı işlemleri (kod üretme, toplam fiyat hesaplama) kolaylaştırır.

---

#### 2. **`backend/productconfig/services/variant_service.py`**
- **Amaç**: Varyantların iş mantığını ve yönetimini sağlar.
- **İşlevler**:
  - Yeni varyant oluşturur ve mevcut varyantları günceller.
  - Varyant detaylarını veritabanından çeker ve istemcinin ihtiyaç duyduğu formatta döndürür.
  - Varyantların silinmesi ve listeleme işlemlerini optimize eder.

---

#### 3. **`backend/productconfig/api/configuration.py`**
- **Amaç**: Konfigürasyon akışını yöneten API endpoint’lerini içerir.
- **İşlevler**:
  - Kullanıcının cevapladığı sorulara göre bir sonraki soruyu dinamik olarak döndürür.
  - Varyant özeti ve geri dönüş işlemleri gibi kritik kullanıcı eylemlerini destekler.
  - Konfigürasyon başlangıcını ve yanıt kaydetme işlemlerini RESTful API üzerinden sağlar.

---

#### 4. **`backend/productconfig/utils/base_helper.py`**
- **Amaç**: Yardımcı sınıfların temel işlevlerini içerir.
- **İşlevler**:
  - Ortak işlemleri (ör. pozitif sayıyı doğrulama) merkezi bir yerde toplar.
  - Yardımcı sınıflar için standart bir yapı sunar.
  - Veri doğrulama ve hata yönetimini basitleştirir.

---

#### 5. **`backend/productconfig/services/price_multiplier_service.py`**
- **Amaç**: Fiyat çarpanı kurallarını uygulamak ve yönetmek.
- **İşlevler**:
  - Belirli seçenek kombinasyonları için fiyat çarpanlarını hesaplar.
  - Fiyat kurallarını değerlendirmek ve tetiklemek için bir mantık sunar.
  - Kullanıcı seçimlerine göre ürünün toplam maliyetini etkiler.

---

#### 6. **`backend/productconfig/models/question.py`**
- **Amaç**: Ürün yapılandırması sırasında kullanılan soruları temsil eder.
- **İşlevler**:
  - Soruların türlerini (ör. metin girişi, tek seçim, çoklu seçim) ve zorunluluk durumlarını tanımlar.
  - Markalar, kategoriler ve ürün modelleri ile ilişkili geçerli soruları belirler.
  - Kullanıcı seçimlerini yönlendirmek için taksonomiler ve bağımlı kurallarla çalışır.

---

#### 7. **`backend/productconfig/services/conditional_options_service.py`**
- **Amaç**: Koşullu seçenekleri değerlendirir ve gösterilmesi gereken seçenekleri belirler.
- **İşlevler**:
  - Kullanıcı seçimlerine bağlı olarak ilgili seçenekleri dinamik olarak sunar.
  - Mantıksal operatörler (VE, VEYA) ve tetikleyici kurallar ile seçenek ilişkilerini yönetir.
  - Kullanıcı deneyimini iyileştirmek için gereksiz seçenekleri gizler.

---

#### 8. **`backend/productconfig/dto/question_context.py`**
- **Amaç**: Soru bağlamını ve uygunluk kontrollerini yönetir.
- **İşlevler**:
  - Kullanıcı seçimlerine göre geçerli olan soruları dinamik olarak belirler.
  - Soruların markalar, kategoriler ve ürün modelleri ile uyumunu kontrol eder.
  - Konfigürasyon sürecindeki bağlam bilgisini optimize eder.

---

#### 9. **`backend/productconfig/api/views.py`**
- **Amaç**: Seçenekler ve varyantlar için temel CRUD işlemlerini yöneten API endpoint’lerini içerir.
- **İşlevler**:
  - Kullanıcıların varyant oluşturma, düzenleme ve silme işlemlerini destekler.
  - Seçeneklerin listeleme ve detaylarını döndürür.
  - Veritabanı sorgularını kullanıcı dostu API'lere dönüştürür.

---

#### 10. **`backend/productconfig/services/option_service.py`**
- **Amaç**: Ürün seçeneklerinin iş mantığını yönetir.
- **İşlevler**:
  - Ürün modellerine bağlı seçenekleri dinamik olarak döndürür.
  - Kullanıcı seçimlerine bağlı olarak toplam fiyatı hesaplar.
  - Seçeneklerin oluşturulması, güncellenmesi ve silinmesini destekler.

---

Bu dosyalar, ProductConfig sisteminin kritik işlevlerini yönetir ve uygulamanın kullanıcı deneyimi ile performansını doğrudan etkiler. Daha fazla detay veya geliştirme planı için her bir dosya üzerinde çalışılabilir. 

### **Kritik Frontend Dosyaları ve Amaçları**

Aşağıda ProductConfig frontend projesindeki kritik dosyalar ve amaçları açıklanmıştır:

---

#### 1. **`frontend/src/components/ProductConfig/store/pcConfigurationSlice.js`**
- **Amaç**: Konfigürasyon akışını ve durumu yönetir.
- **İşlevler**:
  - Kullanıcı cevaplarını kaydeder ve sonraki soruyu dinamik olarak yükler.
  - Redux state üzerinden varyant ID, soru geçmişi ve konfigürasyon durumunu tutar.
  - Async thunk'lar aracılığıyla API ile entegre çalışır.

---

#### 2. **`frontend/src/components/ProductConfig/store/pcVariantSlice.js`**
- **Amaç**: Varyant detaylarını ve listeleme işlemlerini yönetir.
- **İşlevler**:
  - Varyantları oluşturur, günceller, siler ve detaylarını getirir.
  - Redux store'da varyant listesi ve detaylarını tutar.
  - Kullanıcı etkileşimlerine bağlı olarak API çağrıları yapar ve sonucu günceller.

---

#### 3. **`frontend/src/components/ProductConfig/api/pcConfigurationService.js`**
- **Amaç**: Backend API ile iletişim kurar ve konfigürasyonla ilgili işlemleri yönetir.
- **İşlevler**:
  - İlk soru, cevap gönderme ve varyant özeti gibi API çağrılarını gerçekleştirir.
  - Veriyi formatlayarak Redux slice’lara aktarır.
  - Backend ile etkileşim için merkezi bir servis katmanı sağlar.

---

#### 4. **`frontend/src/components/ProductConfig/configuration/PCConfigurationFlow.js`**
- **Amaç**: Kullanıcıların adım adım ürün konfigürasyonu yapmasını sağlar.
- **İşlevler**:
  - Mevcut soruyu veya varyant özetini dinamik olarak gösterir.
  - Kullanıcı yanıtlarını işleyerek sonraki soruya geçiş yapar.
  - Akış kontrolü ve bileşen yönetimi için merkezi bir yapı sunar.

---

#### 5. **`frontend/src/components/ProductConfig/variant/PCVariantList.js`**
- **Amaç**: Kullanıcıların tüm varyantlarını listelemelerini sağlar.
- **İşlevler**:
  - Redux'tan gelen varyant listesini tablo olarak gösterir.
  - Detay görüntüleme, varyant düzenleme ve silme işlemlerini destekler.
  - Filtreleme ve sayfalama gibi kullanıcı deneyimini geliştiren özellikler sunar.

---

#### 6. **`frontend/src/components/ProductConfig/variant/PCVariantDetails.js`**
- **Amaç**: Seçilen bir varyantın detaylarını gösterir.
- **İşlevler**:
  - Proje adı, varyant kodu, açıklama, toplam fiyat ve seçenekleri kullanıcıya sunar.
  - Yazdırma, düzenleme ve yeni varyant oluşturma gibi işlemleri destekler.
  - Redux’tan alınan verileri bileşen içinde işleyerek kullanıcı dostu bir arayüz sunar.

---

#### 7. **`frontend/src/components/ProductConfig/utils/pcHelpers.js`**
- **Amaç**: UI ve iş mantığı için yardımcı fonksiyonlar içerir.
- **İşlevler**:
  - Fiyat ve tarih formatlama gibi yaygın işlemleri sağlar.
  - Seçenekleri sıralama, filtreleme ve arama gibi işlevleri destekler.
  - Varyant kodu ve açıklaması gibi kullanıcıya özel veriler oluşturur.

---

#### 8. **`frontend/src/components/ProductConfig/pages/PCConfigurationPage.js`**
- **Amaç**: Ürün konfigürasyonu sayfasını yönetir.
- **İşlevler**:
  - Kullanıcının mevcut konfigürasyonu düzenlemesini veya yeni bir konfigürasyon başlatmasını sağlar.
  - Redux store ile entegre çalışarak durum güncellemelerini yönetir.
  - Modal pencereleri ile kullanıcıdan onay alır (ör. varyant silme).

---

#### 9. **`frontend/src/components/ProductConfig/pages/PCVariantPage.js`**
- **Amaç**: Bir varyantın detaylarını yönetir ve kullanıcı eylemlerini destekler.
- **İşlevler**:
  - Varyantın tüm detaylarını (ör. proje adı, açıklama, fiyat) görüntüler.
  - Kullanıcıya düzenleme, silme ve yeni varyant oluşturma seçenekleri sunar.
  - Modal ve Redux entegrasyonu ile detaylı kullanıcı etkileşimleri sağlar.

---

#### 10. **`frontend/src/components/ProductConfig/hooks/usePCConfiguration.js`**
- **Amaç**: Konfigürasyon akışını yönetmek için özel bir React Hook sağlar.
- **İşlevler**:
  - İlk soru ve sonraki sorular için API çağrıları yapar.
  - Redux’a gerek kalmadan lokal state üzerinden akış yönetimi sunar.
  - Kullanıcı yanıtlarını işleyerek konfigürasyonun ilerlemesini sağlar.

---

Bu dosyalar, ProductConfig frontend sisteminin temel taşlarını oluşturur ve kullanıcı deneyimi ile iş mantığının başarılı bir şekilde birleşmesini sağlar. Daha fazla detay veya geliştirme planı için her bir dosya özelinde çalışma yapılabilir. 

### **DTO Altında Derin Filtreleme Mantığını Yönetmek**

ProductConfig projesinde **DTO (Data Transfer Object)**, marka, grup, kategori ve ürün modelleri gibi yapıların seçenekler ve sorularla olan ilişkisini dinamik bir şekilde yönetir. Bu yapı, derin filtreleme ve uygulanabilirlik kontrollerini optimize ederek doğru verilerin doğru bağlama ulaştırılmasını sağlar.

#### **Applicable_* Yapısının Mantığı**
- **Amaç**: Marka, grup, kategori ve ürün modellerinin yalnızca geçerli (applicable) seçenekler ve sorularla eşleştirilmesini sağlar.
- **Nasıl Çalışır**:
  - Marka, grup, kategori ve ürün modelleri için `applicable_brands`, `applicable_groups`, `applicable_categories` ve `applicable_product_models` adında ayrı alanlar DTO içinde tutulur.
  - Kullanıcının seçtiği seçeneklere ve yanıtladığı sorulara göre bu alanlar filtrelenir.
  - Derin ilişkilerde, her yapı yalnızca bağlama uygun olan seçenekleri ve soruları döndürür.

---

### **Süreç ve Yapılar**

#### **1. Marka, Grup, Kategori ve Ürün Modellerinin Uygulanabilirliği**
- **`applicable_brands`**: Seçeneklerin veya soruların hangi markalara uygun olduğunu belirler.
  - Örnek: `option.applicable_brands` üzerinden bir seçenek yalnızca belirli markalara gösterilir.
- **`applicable_groups`**: Grupların seçenekler ve sorular üzerindeki filtreleme işlevi.
  - Örnek: `question.applicable_groups` bir sorunun hangi ürün gruplarında görünmesi gerektiğini belirler.
- **`applicable_categories`**: Kategorilerle olan ilişkileri yönetir.
  - Örnek: `option.applicable_categories` belirli kategorilere özgü seçenekleri tanımlar.
- **`applicable_product_models`**: Ürün modellerinin geçerli olduğu durumlar için uygulanır.
  - Örnek: `question.applicable_product_models` bir sorunun yalnızca belirli ürün modellerinde geçerli olmasını sağlar.

---

#### **2. `QuestionContext` Yapısı**
- **Tanım**: Kullanıcı seçimlerine ve bağlamına göre soruların uygunluğunu kontrol eden DTO.
- **İşlevler**:
  - Kullanıcının seçtiği bir seçenek üzerinden bağlamı günceller (`update_from_option`).
  - Sorunun bağlam içinde geçerli olup olmadığını kontrol eder (`is_applicable_for_question`).
- **Örnek Çalışma**:
  ```python
  context.update_from_option(selected_option)
  if context.is_applicable_for_question(question):
      return question
  ```
  - Seçilen bir seçenek üzerinden bağlam güncellenir.
  - Sorunun geçerliliği kontrol edilir ve bağlam uygun değilse soru dışlanır.

---

#### **3. Seçenek ve Sorular İçin Derin Filtreleme**
Her yapının belirli bağlama uygunluk kontrolü:
- **Seçenek Filtreleme**:
  - Kullanıcının seçtiği markalar, kategoriler ve ürün modellerine göre seçenekler filtrelenir.
  - Örnek:
    ```python
    applicable_options = Option.objects.filter(
        applicable_brands__in=user_brands,
        applicable_categories__in=user_categories,
        applicable_product_models__in=user_product_models
    )
    ```
- **Soru Filtreleme**:
  - Soruların markalar, gruplar ve kategoriler ile olan ilişkileri kontrol edilir.
  - Örnek:
    ```python
    applicable_questions = Question.objects.filter(
        applicable_brands__in=context.applicable_brands,
        applicable_categories__in=context.applicable_categories
    )
    ```

---

### **Applicable_* Yapılarının Örnek İşleyişi**
**Senaryo**: Bir kullanıcı belirli bir marka için bir ürün grubu ve kategori seçiyor. 
1. **Marka Seçimi**:
   - Kullanıcının seçtiği marka üzerinden `applicable_brands` filtrelenir.
2. **Grup ve Kategori Seçimi**:
   - Seçili marka ve grubun geçerli kategorileri `applicable_categories` üzerinden belirlenir.
3. **Seçenek ve Soruların Getirilmesi**:
   - Marka, grup ve kategoriye uygun seçenekler ve sorular `applicable_*` alanları üzerinden dinamik olarak döndürülür.

**Kod Örneği**:
```python
def get_filtered_questions_and_options(user_context):
    # Kullanıcının bağlamına göre geçerli soruları getir
    applicable_questions = Question.objects.filter(
        applicable_brands__in=user_context.applicable_brands,
        applicable_groups__in=user_context.applicable_groups,
        applicable_categories__in=user_context.applicable_categories
    )

    # Kullanıcının bağlamına göre geçerli seçenekleri getir
    applicable_options = Option.objects.filter(
        applicable_brands__in=user_context.applicable_brands,
        applicable_categories__in=user_context.applicable_categories
    )

    return applicable_questions, applicable_options
```

---

### **Sonuç**
Applicable_* yapıları, marka, grup, kategori ve ürün modellerinin dinamik olarak seçenekler ve sorularla ilişkilendirilmesini sağlar. Bu yapı sayesinde:
- Kullanıcıya yalnızca bağlama uygun olan içerik gösterilir.
- Gereksiz veriler dışlanarak performans artırılır.
- Kullanıcı deneyimi sade ve optimize edilmiş hale getirilir.

Bu sistem, derin filtreleme mantığını otomatikleştirerek modüler üretim süreçlerinde doğru verinin doğru zamanda sunulmasını mümkün kılar. 
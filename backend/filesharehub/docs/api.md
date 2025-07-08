### File Share Hub Uygulaması Whitepaper

---

#### **Proje Adı**: File Share Hub  
#### **Teknolojiler**: Django REST Framework, React.js  
#### **Amaç**: Kullanıcıların bir ağ üzerindeki belirli bir klasöre sadece okuma (read-only) ve indirme yetkisiyle erişmesini sağlayan bir uygulama geliştirmek. Kullanıcılar dosyaları görüntüleyebilir ve indirebilir, ancak düzenleme veya silme işlemleri yapamaz.

---

### 1. **Giriş**

File Share Hub uygulaması, kurum içi kullanıcıların sadece okuma yetkisiyle belirli bir dizindeki görseller, PDF dosyaları ve ofis dosyalarına erişmesini sağlayan bir platformdur. Kullanıcılar dosyaları indirip görüntüleyebilir, ancak başka bir işlem yapamaz. Bu, kullanıcıların yetkisiz değişiklikler yapmasını engeller ve veri bütünlüğünü sağlar.

---

### 2. **Temel İşlevler**

#### 2.1. **Dosya Görüntüleme**
Kullanıcılar, belirli bir klasörde yer alan tüm dosya ve klasörleri listeleyebilir. Kullanıcılar dosyaların yalnızca metadata bilgilerine (dosya adı, boyut, tipi) erişebilir ve dosyanın küçük bir önizlemesi (thumbnail) ile dosyayı inceleyebilir.

#### 2.2. **Dosya İndirme**
Kullanıcılar, listedeki dosyaları bilgisayarlarına indirebilir. Ancak dosya üzerinde düzenleme, silme veya yeniden yükleme gibi işlemler yapamazlar. Sadece indirme ve okuma işlemlerine izin verilir.

#### 2.3. **Thumbnail Yönetimi**
Uygulama, resim dosyaları için küçük resim önizlemeleri (thumbnail) sunar. İkonlar, dosya tipine göre dinamik olarak atanır ve görüntülenir.

#### 2.4. **Yetki Yönetimi**
Kullanıcıların sisteme sadece read-only erişimi vardır. Backend’de yetki kontrolü yapılır ve kullanıcıların dosya değiştirme yetkisi engellenir. Django REST Framework üzerinde permissions yapılandırması kullanılır.

---

### 3. **Teknik Mimarisi**

#### 3.1. **Backend (Django REST Framework)**

- **Framework**: Django REST Framework
- **Veritabanı**: PostgreSQL
- **Dosya Yönetimi**: Samba veya NFS gibi ağ protokolleri kullanılarak, kullanıcıların dosyalara erişimi sağlanır. Bu dosyalar Ubuntu üzerindeki belirli dizinlerde yer alır (örneğin: `/mnt/gorseller`).
- **API**: Django REST Framework tabanlı bir API oluşturulmuştur. API, dosya listelerini, thumbnail’leri ve dosya indirme işlemlerini yönetir.

##### Backend İşlevleri:

1. **Dosya Listeleme API'si**:
   - İlgili dizinde bulunan dosya ve klasörlerin listesini döndürür.
   - Sadece `GET` metodu ile çalışır.
   - Metadata (dosya adı, boyutu, tipi, son değiştirilme tarihi) sağlar.
   
2. **Dosya İndirme API'si**:
   - Kullanıcının bir dosyayı indirmesine olanak tanır.
   - Dosya indirildikten sonra ilgili loglama yapılır.
   
3. **Thumbnail API'si**:
   - Görsel dosyalar için küçük önizleme resimlerini (thumbnails) döndürür. Diğer dosya tipleri için ikonik gösterim sağlanır.

4. **Yetkilendirme ve Güvenlik**:
   - Kullanıcıların sadece `GET` isteklerini yapmasına izin verilir. Dosya değiştirme yetkisi tamamen devre dışı bırakılmıştır.
   - Kullanıcılar API erişim kontrolü ile sınırlandırılmıştır ve her bir kullanıcıya belirli dizinler üzerinde okuma ve indirme yetkisi tanımlanmıştır.

#### 3.2. **Frontend (React.js)**

- **Framework**: React.js
- **Kullanıcı Arayüzü**: Dosya ve klasörlerin listelenmesi, thumbnail görüntüleme, dosya indirme butonları ile minimal ve işlevsel bir arayüz sunulmaktadır.
- **Küçük Resim (Thumbnail) Yönetimi**: Frontend tarafında, dosya tipine göre thumbnail veya ikon gösterimi yapılır. Örneğin, bir resim dosyası küçük resim olarak gösterilirken, bir PDF dosyası için PDF ikonuyla gösterim yapılır.
- **İşlevsel Bileşenler**:
  - **File List Component**: Dosyaların ve klasörlerin listelendiği bileşen.
  - **Thumbnail Component**: Dosya tipine göre thumbnail veya ikon gösteren bileşen.
  - **File Download Component**: Dosya indirme işlevini yöneten bileşen.

##### Frontend İşlevleri:

1. **Dosya Listeleme**:
   - Kullanıcı mevcut dizinde yer alan dosya ve klasörleri görebilir.
   - İlgili klasöre tıklayarak klasörün alt dizinine inebilir.

2. **Dosya İndirme**:
   - Her dosyanın yanında indirme butonu bulunur. Tıklanarak dosya indirilebilir.

3. **Thumbnail ve İkon Gösterimi**:
   - Resim dosyaları için küçük resim (thumbnail) gösterilir. Diğer dosya türleri için dosya tipine uygun ikonlar gösterilir.

#### 3.3. **Veritabanı (PostgreSQL)**

- **Tablolar**:
  - `filesharehub_filerecord`: Dosya bilgilerini (dosya adı, dosya yolu, yüklenme tarihi vb.) tutan tablo.
  - Veritabanı üzerinden dosya erişimi, kullanıcıların indirdikleri dosyaların loglanması sağlanır.

---

### 4. **Detaylı Kullanım Senaryoları**

#### 4.1. **Dosya Listeleme**
Kullanıcı API'ye bir GET isteği gönderdiğinde, ilgili dizindeki dosya ve klasörler listelenir. Dosyalar için thumbnail’ler ve dosya tipine göre ikonlar gösterilir. Kullanıcı dizinler arasında gezinebilir.

#### 4.2. **Dosya İndirme**
Kullanıcı bir dosyayı indirmek istediğinde, API üzerinden GET isteği yapılır ve dosya kullanıcıya indirilir. İndirilen dosya ile ilgili loglama yapılır.

#### 4.3. **Yetki Kısıtlamaları**
Sistem, sadece okuma ve indirme yetkisi sağlar. Kullanıcıların dosya ekleme, silme veya değiştirme gibi işlemler yapmasına izin verilmez. Django REST API'sinde izinler (permissions) katmanında bu kontroller yapılır.

---

### 5. **Güvenlik ve Yetkilendirme**

- **Kullanıcı Rolleri**: Kullanıcılar sadece okuma ve indirme yetkisine sahiptir.
- **API Güvenliği**: API’ye sadece yetkili kullanıcılar erişebilir. Django Rest Framework’te JWT veya Token Authentication kullanılabilir.
- **Veri Güvenliği**: Sadece yetkilendirilen dizinlere erişim sağlanır.

---

### 6. **Sonuç**

File Share Hub, kullanıcıların güvenli bir şekilde dosyalara erişip indirebileceği, ancak herhangi bir şekilde dosya üzerinde değişiklik yapamayacağı bir yapı sağlar. Uygulamanın temel amacı, dosya paylaşımında veri bütünlüğünü ve güvenliği sağlarken, kullanıcıya sadece dosya görüntüleme ve indirme imkanı sunmaktır. 

Uygulamanın **backend** ve **frontend** mimarisi esnek, modüler ve güvenlik odaklı bir yaklaşım ile geliştirilmiştir. İleride daha fazla özellik eklenerek veya sistem ölçeklendirilerek genişletilebilir.

--- 

Bu whitepaper senin için kapsamlı oldu mu? Eğer başka detaylar eklemek istersen ya da değiştirmek istediğin noktalar varsa, üzerinde çalışabiliriz.



***
whitepaper 01

# FileShareHub: Güvenli ve Sınırlı Erişimli Dosya Paylaşım Platformu

## 1. Giriş

FileShareHub, şirketlerin müşterilerine belirli dosyalara güvenli ve kontrollü erişim sağlayabileceği bir platformdur. Müşteriler, yalnızca indirme yetkisi ile dosyalara erişebilir ve başka hiçbir işlem yapamazlar.

## 2. Amaç

FileShareHub, müşterilerin OpenVPN üzerinden güvenli bir bağlantı kurarak, şirket sunucusunda barındırılan dosyalara erişim sağlamaları için geliştirilmiştir. Müşteriler, Django tabanlı bir web uygulaması üzerinden dosyaları görüntüler ve indirirler. Dosya yükleme veya silme yetkisi sunulmaz.

## 3. Teknolojiler

- **Django**: Backend geliştirme ve API oluşturma.
- **Django Rest Framework**: RESTful API geliştirme.
- **React**: Kullanıcı arayüzü oluşturma.
- **OpenVPN**: Kullanıcıların güvenli bir şekilde sunucuya bağlanması.

## 4. Proje Detayları

1. **OpenVPN Bağlantısı**: Müşteri, şirketin sunduğu OpenVPN bağlantısı ile sunucuya güvenli bir şekilde bağlanır.
2. **Django Tabanlı Giriş**: OpenVPN bağlantısı kurulduktan sonra, müşteri Django tabanlı web uygulamasına giriş yapar.
3. **Dosya Görüntüleme ve İndirme**: Müşteri, "FileShare" bölümüne erişerek, belirli bir IP adresinde barındırılan dosyaları görüntüler ve indirir. Dosya yükleme veya sil

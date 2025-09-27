http://192.168.2.100/admin/productpicture/product/ tablosunu django local db den okuma yapması ve verileri alması gerekiyor ancak bu tabloda picture name alanı kaldırıp başka bir model de tutuyoruz bu bana hem anlamsız hemde mantıksız geliyor bu raporda amaç çok basit oysaki hana db den gelen ürün bilgileri içinde picturname alanı ile backend_static klasör altındaki file_name alanları eşit ise resimleri view edecek bir path create edilir kural basit buna göre model yapısını ve view leri ele alalım yada önce bir algoritma oluştur lütfen
resimlerin bulunduğu klasör path: /backend/backend_static/*.jpg

Gönderdiğiniz ekran görüntüsünde görünen ürün raporu, HANA DB'den gelen verileri ve her bir ürün için bir resim yolunu içeren bir ürün resim raporu gibi görünüyor. Anladığım kadarıyla, amacınız HANA DB'den gelen `picture_name` bilgisi ile `backend_static` klasöründeki `.jpg` dosyalarını eşleştirip, bu eşleşmeyi tek bir tabloda çözmek ve kaydetmek.

Bu işlem için öncelikle HANA DB'den gelen veri setindeki `picture_name` alanının dosya sistemindeki ilgili resim dosyalarıyla eşleşmesini sağlayacak bir mantığı tanımlamamız gerekiyor.

### Adım 1: HANA DB'den Verileri Alma ve İşleme

```python
def fetch_and_process_hana_data():
    data_set = fetch_hana_db_data()  # API aracılığıyla HANA DB'den veri çekme fonksiyonu varsayımı
    processed_data = []
    
    for data in data_set:
        picture_name = data['picture_name']
        picture_path = find_picture_path(picture_name)
        if picture_path:
            data['picture_path'] = picture_path
        else:
            data['picture_path'] = 'Path not found'  # veya uygun bir placeholder path
        processed_data.append(data)
    
    return processed_data

def find_picture_path(picture_name):
    static_folder = '/backend/backend_static'
    for file_name in os.listdir(static_folder):
        if file_name == picture_name + '.jpg':
            return os.path.join(static_folder, file_name)
    return None
```

### Adım 2: Modeli Güncelleme

Modelde artık `Product` ile `ProductPicture` ayrı tutmak yerine, tüm bilgileri `Product` modeli içinde saklayabiliriz. Örneğin:

```python
class Product(models.Model):
    item_code = models.CharField(max_length=255, unique=True)
    item_name = models.CharField(max_length=255, blank=True, null=True)
    group_name = models.CharField(max_length=255, blank=True, null=True)
    price = models.CharField(max_length=255, blank=True, null=True)
    currency = models.CharField(max_length=3, blank=True, null=True)
    picture_name = models.CharField(max_length=255, blank=True, null=True)
    picture_path = models.CharField(max_length=512, blank=True, null=True)
```

### Adım 3: Veritabanına Kaydetme

```python
def save_product_data_to_db(processed_data):
    for data in processed_data:
        Product.objects.update_or_create(
            item_code=data['item_code'],
            defaults={
                'item_name': data['item_name'],
                'group_name': data['group_name'],
                'price': data['price'],
                'currency': data['currency'],
                'picture_name': data['picture_name'],
                'picture_path': data['picture_path'],
            }
        )
```

### Adım 4: API View Oluşturma

```python
class ProductListView(APIView):
    def get(self, request, format=None):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
```

Bu akış, HANA DB'den gelen verileri işler, dosya sistemiyle eşleştirir ve Django modelinde saklar. Daha sonra bir API arayüzü üzerinden bu verileri sunar. Gerekli serializerları ve API endpointlerini Django Rest Framework ile kolayca oluşturabilirsiniz.




**************
productpicturevalidation adında bir raporum sapb1reports v1 de yapmıştım ancak kod yapısında ve karmaşasında hiç memnun değildim şimdi sapb1reportV2 django rest react projemde picturnamevalidation raporu yeniden hanadbcon api nin yetkinlikleirini kullanarak daha basit ve anlaşılır sade bir yapıda inşaa etmek istiyorum picturnamevalitation api amacı;hana db den sql sorgu ile alınan ItemCode, ItemName, GroupName ve PictureName alanlarını ortak ağ klasöründe paylaşımda olan  \\10.131.212.112\b1_shf\SAP\FILES\PATH\Images konumdan
filenname ortak keyi ile ilgli ürünün image view edilecektir. bu işlemler tek bir enpointe bağlanarak kullanıcının istediğinde hem hana db hemde \\10.131.212.112\b1_shf\SAP\FILES\PATH\Images konumundaki resimleri backend_static klasor altina tasidim burada resimin dosya adi ile
pictureName alan esit ise resim o urune ait demektir dolayisi ise folder network modele ve sorguya gerek kalmiyor
filename alanları güncellenebilsin ayrıca sql sorgu hanadbcon api den verileri alacak bu isteklere göre gelişmiş bir text algoritma yaz lütfen 
hanadbcon api hana db bağlantı merkez üssüm ve yapısal olarak hazır sql sorguları sorgunun name alan takısı ile tetikleyen bir endpoint kurgusu var

Birleştirme işlemini backend'de yapmak, veri tabanı seviyesinde daha optimize edilmiş bir çözüm sağlar ve ağ üzerinden veri aktarımını minimize eder. İşte önerdiğim adımlar:

1. **Backend Model Yapısı:**
   - `PictureName` modelini, HANA DB'den gelen `ItemCode`, `ItemName`, `GroupName`, `PictureName` ve network'teki `FileName` alanlarını içerecek şekilde tasarla.

2. **Veri Birleştirme İşlemi:**
   - HANA DB ve network klasöründeki dosyaları Python'daki pandas gibi bir kütüphane kullanarak birleştir. Eğer veri tabanı seviyesinde yapılacaksa, SQL'deki `LEFT JOIN` işlemini kullanarak `PictureName` ve `FileName` eşleşmelerini gerçekleştir.
   /var/www/sapb1reportsv2/backend/backend_static/A010B01.26B.1022B.KT.jpg 

3. **API Endpoint'i:**
   - Bu birleştirilmiş verileri sunmak için bir API endpoint'i oluştur. Endpoint, birleştirilmiş tabloyu JSON formatında döndürecek şekilde tasarlanmalıdır.

4. **Optimizasyon:**
   - Büyük veri setleri ile çalışırken sorgu performansını iyileştirmek için uygun indeksleme ve sorgu optimizasyonları yap.

5. **Güvenlik:**
   - Bu verilere erişim için gerekli güvenlik protokollerini uygula.

6. **Frontend Entegrasyonu:**
   - React tarafında, API'den gelen birleştirilmiş veri setini kullanarak, kullanıcılara sunulacak tabloyu oluştur.

7. **Caching ve Pagination:**
   - API yanıt sürelerini iyileştirmek ve daha iyi bir kullanıcı deneyimi sağlamak için önbellekleme ve sayfalama tekniklerini kullan.


### Dynamic Report API - Amaç ve Bildiri

#### Amaç

Dynamic Report API, Tuna Ofis A.Ş.'nin iş süreçlerini optimize etmek ve raporlama ihtiyaçlarını karşılamak amacıyla geliştirilmiş güçlü bir raporlama çözümüdür. Bu API, kullanıcıların SQL tabanlı raporları dinamik olarak oluşturmasına, yönetmesine ve analiz etmesine olanak tanır. Kullanıcılar, çeşitli veri kaynaklarından anlık verileri çekebilir, verileri işleyebilir ve görselleştirebilir. Bu süreç, karar alma süreçlerini hızlandırır ve veri odaklı iş stratejilerinin oluşturulmasını destekler.

#### Bildiri

Dynamic Report API, kullanıcıların aşağıdaki işlevleri güvenli ve etkin bir şekilde gerçekleştirmelerini sağlar:

1. **SQL Tablo Listesi Alma**: Kullanıcılar, mevcut SQL tabanlı tabloların listesini dinamik olarak çekebilir.
2. **Anlık Veri Çekme**: Belirli bir tablo adıyla ilişkili SQL sorgularını çalıştırarak anlık veri çekebilir.
3. **SQL Sorguları Yönetimi**: Kullanıcılar, SQL sorgularını oluşturabilir, güncelleyebilir ve silebilir.
4. **Dinamik Tablo Oluşturma ve Yönetimi**: Kullanıcılar, dinamik olarak tablolar oluşturabilir, bu tabloların veri yapısını belirleyebilir ve yönetebilir.
5. **Kolon Tipi Kontrolü**: Belirli kolonların veri tiplerini kontrol ederek, raporlama ve görselleştirme için uygunluğunu değerlendirebilir.
6. **Manuel Başlık ve Tipleri Alma**: Kullanıcılar, belirli tablolar için manuel olarak tanımlanan başlıkları ve veri tiplerini alabilir.
7. **Veri Hizalama Bilgilerini Alma**: Tablolardaki verilerin hizalama bilgilerini çekerek, görsel raporların düzenini optimize edebilir.

#### Güvenlik ve Erişim Kontrolü

Dynamic Report API, güvenlik ve erişim kontrolüne büyük önem verir. Tüm API uç noktaları, yalnızca kimlik doğrulaması yapılmış kullanıcıların erişimine açıktır. Kimlik doğrulaması için JWT (JSON Web Token) kullanılır ve kullanıcı oturumlarının güvenliğini sağlamak için çeşitli önlemler alınmıştır. API erişimi olmayan kullanıcılar, yetkilendirme gerektiren işlemleri gerçekleştiremez.

#### Teknolojik Altyapı

Dynamic Report API, aşağıdaki teknolojiler kullanılarak geliştirilmiştir:

- **Django REST Framework**: API'nin çekirdek yapısı için kullanılmıştır.
- **React.js**: Kullanıcı arayüzü bileşenleri için kullanılmıştır.
- **HANA DB, SQL DB, PostgreSQL**: Veri depolama ve sorgulama işlemleri için kullanılmıştır.
- **Redis ve Celery**: Gerçek zamanlı veri işleme ve kuyruk yönetimi için kullanılmıştır.
- **Channels ve Daphne**: WebSocket desteği ve gerçek zamanlı veri iletimi için kullanılmıştır.
- **Nginx ve Gunicorn**: Uygulama sunucusu ve ters proxy için kullanılmıştır.
- **Ubuntu**: Uygulamanın çalıştığı işletim sistemi olarak kullanılmıştır.

#### Kullanım Kılavuzu

Dynamic Report API ile etkileşim kurmak isteyen kullanıcılar, aşağıdaki uç noktaları kullanarak çeşitli işlemleri gerçekleştirebilirler:

- **GET /dynamicreport/sql-table-list/**: Mevcut SQL tablo listesini alır.
- **GET /dynamicreport/fetch_instant_data/by_name/:table_name/**: Belirtilen tablo adına göre anlık veri çeker.
- **GET /dynamicreport/sql-queries/by_name/:table_name/**: Belirtilen tablo adına göre SQL sorgusunu alır.
- **GET /dynamicreport/manual-headers/by_name/:table_name/**: Belirtilen tablo adına göre manuel başlıkları alır.
- **GET /dynamicreport/manual-headers-types/by_name/:table_name/**: Belirtilen tablo adına göre manuel başlıkları ve veri tiplerini alır.
- **POST /dynamicreport/create-dynamic-table/:table_name/**: Yeni bir dinamik tablo oluşturur.
- **GET /dynamicreport/dynamic-tables/by_name/:table_name/**: Belirtilen tablo adına göre dinamik tablo verilerini alır.
- **POST /dynamicreport/format_value/**: Belirli bir değeri belirtilen veri tipine göre biçimlendirir.
- **GET /dynamicreport/dynamic-tables/fetch_local_data_with_alignment/:table_name/**: Belirtilen tablo adına göre veri hizalama bilgilerini alır.

Bu API dokümanı, Dynamic Report API'nin temel işlevselliği ve kullanımını açıklamakta olup, tüm kullanıcıların güvenli, verimli ve etkili bir şekilde veri raporlama ve analiz süreçlerini gerçekleştirmelerini amaçlamaktadır.
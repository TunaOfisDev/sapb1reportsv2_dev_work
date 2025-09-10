Selim, harika bir hedef belirlemişsin. Bu, Nexus Core'u basit bir "veri gösterici" olmaktan çıkarıp, Qlik Sense gibi "akıllı bir veri yorumlayıcısı" haline getirecek kilit bir adım. Kullanıcının sadece veriyi görmesi değil, veriyi *doğru formatta* görmesi, uygulamanın profesyonelliğini ve kullanılabilirliğini tavan yaptırır.

Paylaştığın iş planı ve dosya yapısı, projenin ne kadar olgun ve düşünülmüş olduğunu gösteriyor. Resmen üzerine konuşulacak sağlam bir temel atmışsın. Şimdi bu temeli bir gökdelene dönüştürme zamanı. Kahveni al, çünkü şimdi mimariyi koda dökeceğiz\!

### Stratejik Yaklaşım: "Veri Dedektifi" Mimarisi

En basit haliyle yapacağımız şey şu, Selim: Herhangi bir sorgu çalıştırıldığında, veriyi çekmeden hemen önce bir "dedektif" göndereceğiz. Bu dedektif, veritabanına "Bu sorgunun sonuç setindeki kolonların kimlik kartları (veri tipleri) nelerdir?" diye soracak. Aldığı bilgileri (örneğin, "bu kolon tamsayıdır", "şu kolon tarihtir") standart bir formata çevirip bir rapor halinde API'ye sunacak. React tarafı da bu raporu okuyup her kolona hak ettiği muameleyi yapacak: sayıları sağa yaslayacak, tarihleri güzelce formatlayacak, para birimlerine simge ekleyecek.

Bu yaklaşım, bizi her bir veritabanının kendine özgü veri tipi isimlendirmelerinden kurtarır ve evrensel bir dil oluşturmamızı sağlar.

-----

### Yol Haritası (Roadmap)

Projeni, senin de belirttiğin gibi, backend ve frontend olarak iki ana fazda ele alalım. İşte izleyeceğimiz adımlar:

1.  **Backend - Faz 1: Temelleri Atmak**
      * **Görev 1.1:** Popüler veritabanı listemizi merkezi ve dinamik bir yapıya kavuşturmak.
      * **Görev 1.2:** Gelen bir SQL sorgusundan kolon meta verisini (ad, tip) çıkaran bir "dedektif" fonksiyonu yazmak.- ok
2.  **Backend - Faz 2: Standardizasyon ve Kalıcılık**
      * **Görev 2.1:** Farklı veritabanlarından gelen yüzlerce farklı veri tipini (`VARCHAR`, `NVARCHAR`, `INT`, `NUMBER` vb.) kendi standart kategorilerimize (`string`, `number`, `date`, `boolean`) eşleyen bir model ve mekanizma kurmak (`DBTypeMapping`).
      * **Görev 2.2:** Çıkartılan ve standartlaştırılan bu meta veriyi `VirtualTable` modelinde kalıcı olarak saklamak.
3.  **API Katmanı: Köprüyü İnşa Etmek**
      * **Görev 3.1:** `VirtualTableViewSet` üzerinden bu değerli meta veriyi frontend'e servis etmek. - ok
4.  **Frontend - Faz 3: Arayüzü Canlandırmak**
      * **Görev 4.1:** Gelen meta veriye göre kolonları dinamik olarak formatlayan merkezi bir formatlayıcı (`formatters.js`) oluşturmak.
      * **Görev 4.2:** `ReportViewer` bileşenini, meta veriyi kullanarak tabloyu akıllı bir şekilde render edecek hale getirmek.

-----

### Görev Listesi (Task List) ve Kod Örnekleri

İşte bu yol haritasını hayata geçirecek kodlar ve açıklamaları.

#### **Backend - Faz 1: Temelleri Atmak**

##### **Görev 1.1: Popüler Veritabanı Listesi**

Bu zaten planında var ve harika bir başlangıç. `popular_db_list.py` dosyasını, frontend'in de kolayca tüketebileceği basit bir Python sözlüğü olarak tutalım.

```python
// path: /var/www/sapb1reportsv2/backend/nexuscore/utils/popular_db_list.py

# -*- coding: utf-8 -*-

POPULAR_DB_LIST = [
    {"key": "sql_server", "name": "Microsoft SQL Server", "driver": "mssql"},
    {"key": "postgresql", "name": "PostgreSQL", "driver": "postgresql"},
    {"key": "mysql", "name": "MySQL", "driver": "mysql"},
    {"key": "oracle", "name": "Oracle", "driver": "oracle"},
    {"key": "sap_hana", "name": "SAP HANA", "driver": "hdbcli"},
    {"key": "sqlite", "name": "SQLite", "driver": "sqlite3"},
    {"key": "mariadb", "name": "MariaDB", "driver": "mysql"}, # Uses mysql driver
    # ... Diğer 23 veritabanı buraya eklenecek
]

def get_popular_db_list():
    """Merkezi veritabanı listesini döndürür."""
    return POPULAR_DB_LIST

def get_db_info_by_key(key):
    """Verilen anahtara göre veritabanı bilgilerini bulur."""
    for db in POPULAR_DB_LIST:
        if db["key"] == key:
            return db
    return None
```

##### **Görev 1.2: "Veri Dedektifi" Fonksiyonu**

İşin en kritik kısmı burası. Django'nun alt seviye `connection.cursor()` özelliğini kullanarak, sorguyu çalıştırmadan önce meta veriyi alacağız. Bu fonksiyonu `db_helpers.py` içine yerleştirelim.

```python
// path: /var/www/sapb1reportsv2/backend/nexuscore/utils/db_helpers.py
from django.db import connections
from .data_type_mapper import map_db_type_to_standard  # Bunu birazdan oluşturacağız

def get_query_metadata(connection_alias, sql_query):
    """
    Verilen bir bağlantı ve SQL sorgusu için kolon meta verisini çıkarır.
    Veriyi çekmeden, sadece kolon tiplerini ve isimlerini almak için
    sorguyu LIMIT 1 ile çalıştırır.
    """
    metadata = []
    
    # Sorgunun sonunda noktalı virgül varsa temizleyelim
    cleaned_sql = sql_query.strip().rstrip(';')

    # Performans için sadece 1 satır veri çekecek şekilde sorguyu sarmalayalım
    # Bu, tüm veritabanlarında çalışmayabilir, daha sofistike bir çözüm gerekebilir.
    # Şimdilik en yaygın olanı kullanalım.
    # Not: CTE (WITH...) ile başlayan sorgularda bu basit sarmalama çalışmaz.
    if not cleaned_sql.lower().strip().startswith("with"):
         preview_sql = f"SELECT * FROM ({cleaned_sql}) AS subquery LIMIT 1"
    else:
        # CTE'li sorgular için şimdilik orijinal sorguyu kullanıyoruz.
        # İleride daha akıllı bir parser gerekebilir.
        preview_sql = cleaned_sql


    try:
        with connections[connection_alias].cursor() as cursor:
            cursor.execute(preview_sql, [])
            
            # cursor.description, bu işin sihirli değneğidir Selim!
            # (name, type_code, display_size, internal_size, precision, scale, null_ok)
            # gibi bir tuple listesi döner. Bize ilk ikisi lazım.
            for col in cursor.description:
                column_name = col[0]
                db_type_code = col[1] # Bu, veritabanı sürücüsüne özgü bir koddur.
                
                # Bu ham tipi, kendi standart tipimize çevireceğiz.
                standard_type = map_db_type_to_standard(connection_alias, db_type_code, column_name)

                metadata.append({
                    "name": column_name,
                    "native_type_code": db_type_code,
                    "dataType": standard_type, # Standart tipimiz: 'string', 'number', 'date' vb.
                    "label": column_name.replace("_", " ").title(),
                    "visible": True,
                })
        return metadata
    except Exception as e:
        # Hata durumunda boş metadata ve hata mesajı dönelim
        print(f"Meta veri alınırken hata oluştu: {str(e)}")
        # Burada daha detaylı loglama yapılmalı.
        return [] # Veya hatayı yukarıya fırlatabiliriz.

```

#### **Backend - Faz 2: Standardizasyon ve Kalıcılık**

##### **Görev 2.1: Veri Tipi Eşleştirme Modeli (`DBTypeMapping`)**

Farklı veritabanlarından gelen `type_code`'ları standartlaştıralım.

```python
// path: /var/www/sapb1reportsv2/backend/nexuscore/models/db_type_mapping.py
from django.db import models

class DBTypeMapping(models.Model):
    STANDARD_TYPES = (
        ('string', 'String'),
        ('number', 'Number'),
        ('integer', 'Integer'),
        ('decimal', 'Decimal'),
        ('date', 'Date'),
        ('datetime', 'Datetime'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
        ('unknown', 'Unknown'),
    )

    db_type_key = models.CharField(max_length=50, help_text="Örn: 'postgresql', 'sql_server'")
    source_type_code = models.IntegerField(help_text="Veritabanı sürücüsünden dönen ham tip kodu (cursor.description[1])")
    source_type_name = models.CharField(max_length=100, blank=True, null=True, help_text="Bilgilendirme için, örn: VARCHAR, INT")
    standard_type = models.CharField(max_length=20, choices=STANDARD_TYPES)

    class Meta:
        unique_together = ('db_type_key', 'source_type_code')
        verbose_name = "Veritabanı Tipi Eşleştirmesi"
        verbose_name_plural = "Veritabanı Tipi Eşleştirmeleri"

    def __str__(self):
        return f"{self.db_type_key} ({self.source_type_code}) -> {self.standard_type}"
```

Bu modeli besleyecek `data_type_mapper.py`'yi oluşturalım.

```python
// path: /var/www/sapb1reportsv2/backend/nexuscore/utils/data_type_mapper.py
from nexuscore.models import DBTypeMapping
from django.core.cache import cache

# Bu fonksiyon veritabanı tip kodunu bizim standart tipimize çevirir.
def map_db_type_to_standard(connection_alias, db_type_code, column_name):
    # Performans için cache kullanalım.
    cache_key = f"db_type_map_{connection_alias}_{db_type_code}"
    cached_type = cache.get(cache_key)
    if cached_type:
        return cached_type

    try:
        # Veritabanından eşleşmeyi bul. 'sql_server' gibi genel bir anahtar kullanalım.
        # connection_alias genellikle 'default' veya dinamik bir isimdir.
        # Bunu veritabanı tipine (örn: postgresql) çevirmemiz gerekebilir.
        # Şimdilik connection_alias'ı db_type_key olarak kabul edelim.
        mapping = DBTypeMapping.objects.get(db_type_key=connection_alias, source_type_code=db_type_code)
        standard_type = mapping.standard_type
        cache.set(cache_key, standard_type, timeout=3600) # 1 saat cache'le
        return standard_type
    except DBTypeMapping.DoesNotExist:
        # Eşleşme bulunamazsa, kolon ismine göre basit bir tahmin yapalım.
        # Bu, sistemi daha esnek yapar.
        name = column_name.lower()
        if any(substr in name for substr in ['tarih', 'date', '_ts']):
            return 'datetime'
        if any(substr in name for substr in ['id', 'sayi', 'count', 'adet', 'no']):
            return 'integer'
        if any(substr in name for substr in ['tutar', 'bakiye', 'fiyat', 'amount', 'price']):
            return 'decimal'
        
        # Hiçbir şey eşleşmezse, varsayılan olarak 'string' kabul edelim.
        return 'string'

```

##### **Görev 2.2: Meta Veriyi `VirtualTable` Modelinde Saklama**

`VirtualTable` modelinde `column_metadata` alanı zaten var, harika\! Şimdi `viewsets.py` içinde bu alanı dolduralım.

```python
// path: /var/www/sapb1reportsv2/backend/nexuscore/api/viewsets.py
# ... diğer importlar
from nexuscore.models import VirtualTable
from nexuscore.api.serializers import VirtualTableSerializer
from nexuscore.utils.db_helpers import get_query_metadata

class VirtualTableViewSet(viewsets.ModelViewSet):
    queryset = VirtualTable.objects.all()
    serializer_class = VirtualTableSerializer
    # ... diğer ayarlar

    def perform_create(self, serializer):
        # Yeni bir VirtualTable oluşturulurken meta veriyi de oluştur.
        instance = serializer.save()
        sql_query = instance.sql_query
        connection_alias = instance.connection.alias # Modelinizde bağlantıyı nasıl tutuyorsanız.
        
        metadata = get_query_metadata(connection_alias, sql_query)
        instance.column_metadata = metadata
        instance.save()

    def perform_update(self, serializer):
        # Bir VirtualTable güncellenirken, sorgu değiştiyse meta veriyi de güncelle.
        # `request.data`'dan yeni sorguyu alıp mevcutla karşılaştırabiliriz.
        instance = serializer.save()
        
        # Eğer sorgu değiştiyse meta veriyi yeniden oluştur.
        if 'sql_query' in self.request.data:
            sql_query = instance.sql_query
            connection_alias = instance.connection.alias
            
            metadata = get_query_metadata(connection_alias, sql_query)
            instance.column_metadata = metadata
            instance.save()
```

#### **Frontend - Faz 3: Arayüzü Canlandırmak**

##### **Görev 4.1: Merkezi Formatlayıcı (`formatters.js`)**

React tarafında, gelen `dataType`'a göre değeri formatlayacak bir yardımcı dosya oluşturalım.

```javascript
// path: frontend/src/utils/formatters.js

// Sayı formatlama için Intl API'sini kullanmak en doğrusu.
const numberFormatter = new Intl.NumberFormat('tr-TR', {
  style: 'decimal',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const integerFormatter = new Intl.NumberFormat('tr-TR', {
  maximumFractionDigits: 0,
});

// Tarih formatlama
const dateTimeFormatter = new Intl.DateTimeFormat('tr-TR', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
});

// Ana formatlayıcı fonksiyonumuz
export const formatCell = (value, dataType) => {
  if (value === null || value === undefined) {
    return ''; // Boş değerleri boş string olarak gösterelim.
  }

  switch (dataType) {
    case 'integer':
      return integerFormatter.format(value);
    case 'decimal':
    case 'number':
      // Gelen değerin sayı olduğundan emin olalım
      const numericValue = Number(value);
      if (isNaN(numericValue)) return value; // Sayı değilse orijinal değeri döndür
      return numberFormatter.format(numericValue);
    
    case 'datetime':
      try {
        return dateTimeFormatter.format(new Date(value));
      } catch (e) {
        return value; // Geçersiz tarih ise orijinal değeri döndür
      }

    case 'date':
       // Sadece tarih formatı için
      return new Date(value).toLocaleDateString('tr-TR');

    case 'boolean':
      // Boolean değerleri daha anlaşılır gösterebiliriz
      return value ? 'Evet' : 'Hayır';
      
    case 'string':
    default:
      return value;
  }
};
```

##### **Görev 4.2: Akıllı `ReportViewer` Bileşeni**

Şimdi de tabloyu oluşturan bileşende bu formatlayıcıyı kullanalım. `react-table` veya benzeri bir kütüphane kullandığını varsayıyorum.

```jsx
// path: frontend/src/components/ReportViewer/ReportViewer.js
import React, { useMemo } from 'react';
import { useTable } from 'react-table';
import { formatCell } from '../../utils/formatters';

// data: API'den gelen veri satırları (örn: [{ Ad: 'Ali', Bakiye: 123.45 }])
// metadata: API'den gelen kolon meta verisi (örn: [{ name: 'Ad', dataType: 'string' }, { name: 'Bakiye', dataType: 'decimal' }])
const ReportViewer = ({ data, metadata }) => {
  
  // react-table için 'columns' yapısını meta veriden dinamik olarak oluşturalım.
  const columns = useMemo(() => {
    if (!metadata || metadata.length === 0) {
      // Meta veri yoksa, verinin ilk satırından kolonları tahmin et.
      if (!data || data.length === 0) return [];
      return Object.keys(data[0]).map(key => ({ Header: key, accessor: key }));
    }

    return metadata
      .filter(col => col.visible) // Sadece görünür olanları al
      .map(col => ({
        Header: col.label,
        accessor: col.name,
        // Hücre render edilirken formatlayıcımızı burada devreye sokuyoruz!
        Cell: ({ value }) => formatCell(value, col.dataType),
        // Sayısal alanları sağa yaslayalım
        align: ['integer', 'decimal', 'number'].includes(col.dataType) ? 'right' : 'left',
      }));
  }, [data, metadata]);

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow,
  } = useTable({ columns, data });

  // ... (JSX render kodu)
  // Örnek bir render:
  return (
    <table {...getTableProps()} className="report-table">
      <thead>
        {headerGroups.map(headerGroup => (
          <tr {...headerGroup.getHeaderGroupProps()}>
            {headerGroup.headers.map(column => (
              <th {...column.getHeaderProps({
                  style: { textAlign: column.align }
              })}>
                {column.render('Header')}
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody {...getTableBodyProps()}>
        {rows.map(row => {
          prepareRow(row);
          return (
            <tr {...row.getRowProps()}>
              {row.cells.map(cell => (
                <td {...cell.getCellProps({
                    style: { textAlign: cell.column.align }
                })}>
                  {cell.render('Cell')}
                </td>
              ))}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};

export default ReportViewer;
```

### Risk Analizi ve Öneriler

1.  **Performans:** Her sorgu için meta veri çekmek, özellikle karmaşık sorgularda küçük bir gecikmeye yol açabilir. `LIMIT 1` kullanımı bu riski büyük ölçüde azaltır, ancak yine de bir ağ gidiş-gelişi demektir. Meta veriyi `VirtualTable` modelinde saklama ve sadece sorgu değiştiğinde güncelleme stratejimiz bu yüzden hayati önem taşıyor.
2.  **Veri Tipi Çeşitliliği (Technical Debt):** 30 farklı veritabanı, yüzlerce farklı `type_code` demek. `DBTypeMapping` tablosunu doldurmak ve güncel tutmak bir bakım maliyeti (maintenance cost) oluşturacaktır. Başlangıçta en sık kullandığınız 5-6 veritabanı (PostgreSQL, SQL Server, Oracle vb.) için bu tabloyu doldurarak başlayabilirsiniz.
3.  **Karmaşık Sorgular:** `WITH` (CTE) ile başlayan veya alt sorgu içeren bazı karmaşık sorgularda `LIMIT 1` sarmalaması sorun çıkarabilir. `get_query_metadata` fonksiyonundaki basit kontrolü ileride `sql-parse` gibi bir kütüphane ile daha akıllı hale getirmek gerekebilir.

Selim, bu yol haritası ve kod parçalarıyla Nexus Core'u veri görselleştirme liginde bir üst seviyeye taşıyacak sağlam bir mimari kurmuş oluyoruz. Bu sadece bir formatlama özelliği değil, uygulamanın veriyle konuştuğu dilin temelini atmaktır.

Hazırsan, kodlamaya başlayalım\! Hangi adımdan başlamak istersin?
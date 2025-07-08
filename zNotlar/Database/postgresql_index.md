sudo -u postgres psql
\c sapb1reports_v2

-- İndeksler
CREATE INDEX idx_option_name ON productconfig_option(name);
CREATE INDEX idx_option_is_active ON productconfig_option(is_active);
CREATE INDEX idx_option_price_modifier ON productconfig_option(price_modifier);
CREATE INDEX idx_option_type_active ON productconfig_option(option_type, is_active);

CREATE INDEX idx_question_category_type ON productconfig_question(category_type);
CREATE INDEX idx_question_order_val ON productconfig_question("order");

CREATE INDEX idx_variant_code ON productconfig_variant(variant_code);
CREATE INDEX idx_variant_status ON productconfig_variant(status);
CREATE INDEX idx_variant_created ON productconfig_variant(created_at);

CREATE INDEX idx_option_brand_fk ON productconfig_option_applicable_brands(brand_id);
CREATE INDEX idx_option_category_fk ON productconfig_option_applicable_categories(category_id);
CREATE INDEX idx_option_group_fk ON productconfig_option_applicable_groups(productgroup_id);
CREATE INDEX idx_option_model_fk ON productconfig_option_applicable_product_models(productmodel_id);

-- VACUUM ANALYZE
VACUUM ANALYZE productconfig_option;
VACUUM ANALYZE productconfig_question;
VACUUM ANALYZE productconfig_variant;
VACUUM ANALYZE productconfig_option_applicable_brands;
VACUUM ANALYZE productconfig_option_applicable_categories;
VACUUM ANALYZE productconfig_option_applicable_groups;
VACUUM ANALYZE productconfig_option_applicable_product_models;


PostgreSQL’de oluşturduğunuz indekslerin durumunu ve performansını analiz etmek için `pg_stat_user_indexes` ve `pg_index` sistem kataloglarını kullanabilirsiniz. Ayrıca `VACUUM ANALYZE` işlemi sonrasında indekslerin etkinliğini görmek için bu araçlar oldukça faydalıdır.

Aşağıdaki adımları izleyerek indekslerin durumunu kontrol edebilirsiniz:

---

### **1. İndekslerin Durumunu Görüntüleme**

İndekslerin kullanım istatistiklerini görmek için şu sorguyu çalıştırabilirsiniz:

```sql
SELECT
    schemaname,
    relname AS table_name,
    indexrelname AS index_name,
    idx_scan AS index_scans,        -- İndeksin kaç kez kullanıldığını gösterir
    idx_tup_read AS tuples_read,   -- İndeksle kaç satır okunduğunu gösterir
    idx_tup_fetch AS tuples_fetched -- İndeksle kaç satır alındığını gösterir
FROM
    pg_stat_user_indexes
ORDER BY
    idx_scan DESC; -- En sık kullanılan indeksler üstte görünür
```

---

### **2. Belirli Bir Tablo için İndeksleri Kontrol Etme**

Belirli bir tablo üzerindeki indeksleri görmek için:

```sql
SELECT
    indexname,
    indexdef
FROM
    pg_indexes
WHERE
    tablename = 'productconfig_option';
```

Bu sorgu, `productconfig_option` tablosundaki tüm indekslerin adlarını ve tanımlarını gösterir.

---

### **3. İndeksin Bloat Durumunu Kontrol Etme**

İndekslerin şişme (`bloat`) durumunu analiz etmek için `pgstattuple` modülünü kullanabilirsiniz. Bu modül PostgreSQL üzerinde varsayılan olarak gelmez; yüklemek için aşağıdaki komutu kullanabilirsiniz:

```bash
sudo apt install postgresql-contrib
```

Ardından, bir tablo veya indeksin bloat durumunu kontrol etmek için:

```sql
SELECT * FROM pgstattuple('idx_option_name');
```

---

### **4. İndeks ve Tablo Boyutlarını Kontrol Etme**

İndekslerin boyutunu görmek için şu sorguyu kullanabilirsiniz:

```sql
SELECT
    indexname AS index_name,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM
    pg_stat_user_indexes
WHERE
    schemaname = 'public';
```

---

### **5. İndeks Kullanımını Geliştirme**

- **`REINDEX` Kullanımı:** İndekslerin zamanla şişmesi veya verimsiz hale gelmesi durumunda, yeniden oluşturabilirsiniz:
  ```sql
  REINDEX TABLE productconfig_option;
  ```

- **`VACUUM ANALYZE`:** Tablolar üzerinde `VACUUM ANALYZE` işlemi yaptıktan sonra, optimizer'ın daha doğru istatistiklerle çalışmasını sağlarsınız. Daha önce çalıştırdığınız gibi:
  ```sql
  VACUUM ANALYZE productconfig_option;
  ```

---

### **6. Örnek Çıktı**
`pg_stat_user_indexes` sorgusunun bir örnek çıktısı şöyle görünebilir:

| **schemaname** | **table_name**           | **index_name**               | **index_scans** | **tuples_read** | **tuples_fetched** |
|----------------|--------------------------|------------------------------|-----------------|-----------------|--------------------|
| public         | productconfig_option     | idx_option_name              | 1050            | 3200            | 2500               |
| public         | productconfig_question   | idx_question_order_val       | 500             | 1200            | 1000               |
| public         | productconfig_variant    | idx_variant_created          | 200             | 800             | 750                |

---

### **Sonuç**
Bu adımları kullanarak oluşturduğunuz indekslerin durumunu ve kullanım sıklığını analiz edebilirsiniz. En sık kullanılan indeksler, optimize etmek veya yeniden oluşturmak için en iyi adaylardır. Eğer herhangi bir indeksin kullanım istatistiği düşükse (`index_scans` = 0 gibi), o indeksi kaldırmayı düşünebilirsiniz. 
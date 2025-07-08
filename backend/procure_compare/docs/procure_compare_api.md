# File: procure_compare/docs/procure_compare_api_whitepaper.md

# ProcureCompare API Whitepaper

## Amaç

`ProcureCompare API`, SAP HANA üzerinde bulunan satınalma siparişleri ile bu siparişlerden önce alınmış teklif belgelerindeki fiyat verilerini karşılaştırmak amacıyla geliştirilmiştir. Bu sistem, karar destek süreçlerini iyileştirerek daha bilinçli ve maliyet etkin satınalma kararlarının alınmasına yardımcı olmayı hedefler.

---

##  Genel Yapı

API, Django + DRF altyapısı ile geliştirilmektedir ve React.js ile tasarlanacak olan arayüz üzerinden erişilecektir. Backend tarafında veriler PostgreSQL'e senkronize edilmektedir. Veriler doğrudan SAP HANA'dan çekilmekte, işlenmekte ve local veri tabanına aktarılmaktadır.

> Her veri senkronizasyon işleminde PostgreSQL'deki eski veriler tamamen silinir ve SAP HANA'dan gelen yeni veri ile güncellenir.

---

## Mimaride Kullanılan Katmanlar

- **API**  
  `procure_compare/api/`: API endpoint’lerinin bulunduğu katman.

- **Models**  
  `procure_compare/models/`: `PurchaseOrder`, `PurchaseQuote`, `PurchaseComparison` modellerini içerir.

- **Services**  
  `procure_compare/services/`: SAP HANA bağlantısı, veri dönüştürme ve senkronizasyon işlemlerini yöneten servisler.

- **Tasks**  
  `procure_compare/tasks/`: Cronjob veya Celery üzerinden çalışacak zamanlanmış görevler.

- **Docs**  
  `procure_compare/docs/`: Teknik ve operasyonel dökümantasyonların bulunduğu klasör.

---

##  Backend Yapısı

> Bu bölüme backend klasör yapısı ve genel uygulama dosya hiyerarşisini ekleyebilirsin.

---

## SQL Sorgusu

> Aşağıya HANA'dan kullanılan orijinal SQL sorgusunu ekleyebilirsin.

---

## Güvenlik ve Erişim

- Tüm veri çekme işlemleri token bazlı güvenlik ile korunmaktadır.
- SAP HANA API erişimi `Bearer Token` üzerinden doğrulanır.
- Zaman aşımı ve hata yönetimi `loguru` ile loglanır.

---

##  Kullanım Senaryoları

- Sipariş ve teklif fiyatlarının karşılaştırılması
- En düşük teklifin tespiti
- Tedarikçi performans analizi
- Maliyet tasarrufu fırsatlarının belirlenmesi

---

##  Notlar

- API veri modeli HANA sorgusuna birebir sadık kalınarak oluşturulmuştur.
- Geliştirme QuantumStack mimari yapısına uygun olarak modüler gerçekleştirilmiştir.
- İlerleyen aşamada teklif/sipariş karşılaştırmalarında grafiksel destekli karar modülleri planlanmaktadır.

---

--sql sorgusu
--procure_compare
WITH RefData AS (
    SELECT 
        "DocEntry",
        '[' || STRING_AGG('"' || CAST("RefDocNum" AS NVARCHAR) || '"', ',') || ']' AS "ReferansTeklifler"
    FROM "TUNADB24"."POR21"
    WHERE "RefObjType" = '540000006'
    GROUP BY "DocEntry"
),

RefPriceData AS (
    SELECT 
        P21."DocEntry" AS "SiparisDocEntry",
        PQT1."ItemCode",
        '{' || STRING_AGG(
            '"' || LEFT(OPQT."CardName", 20) || '": "' ||
            CAST(PQT1."Price" AS NVARCHAR) || ' ' || PQT1."Currency" ||
            ' (Kur: ' || CAST(COALESCE(PQT1."Rate", 1) AS NVARCHAR) || ')"'
        , ', ') || '}' AS "TeklifFiyatlariJSON"
    FROM "TUNADB24"."POR21" P21
    JOIN "TUNADB24"."OPQT" OPQT 
        ON P21."RefDocNum" = OPQT."DocNum"
    JOIN "TUNADB24"."PQT1" PQT1 
        ON OPQT."DocEntry" = PQT1."DocEntry"
       AND EXISTS (
           SELECT 1 FROM "TUNADB24"."POR1" R
           WHERE R."DocEntry" = P21."DocEntry"
             AND R."ItemCode" = PQT1."ItemCode"
       )
    WHERE P21."RefObjType" = '540000006'
    GROUP BY P21."DocEntry", PQT1."ItemCode"
),

DetailData AS (
    SELECT
        T0."DocEntry" || '-' || R."LineNum" || '-' || 
        ROW_NUMBER() OVER (PARTITION BY T0."DocEntry", R."LineNum" ORDER BY T0."DocNum" DESC) AS "UniqDetailNo",
        T0."DocNum"  AS "BelgeNo",
        T0."CardCode" AS "TedarikciKod",
        T0."CardName" AS "TedarikciAd",
        TO_CHAR(T0."DocDate", 'YYYY-MM-DD') AS "BelgeTarih",
        TO_CHAR(T0."DocDueDate", 'YYYY-MM-DD') AS "TeslimTarih",
        CASE WHEN T0."DocStatus" = 'O' THEN 'Açık' ELSE 'Kapalı' END AS "BelgeStatus",
        T0."Comments" AS "BelgeAciklamasi",
        T0."Address2" AS "SevkAdres",
        OITB."ItmsGrpNam" AS "KalemGrup",
        CASE WHEN R."LineStatus" = 'O' THEN 'Açık' ELSE 'Kapalı' END AS "SatirStatus",
        R."LineNum" AS "SatirNo",
        R."ItemCode" AS "KalemKod",
        R."Dscription" AS "KalemTanimi",
        R."UomCode" AS "Birim",
        COALESCE(R."Quantity", 0) AS "SipMiktar",
        CASE WHEN R."Currency" = 'TRY' THEN 1 ELSE COALESCE(R."Rate", 1) END AS "DetayKur",
        COALESCE(R."Currency", 'TRY') AS "DetayDoviz",
        COALESCE(R."Price", 0) AS "NetFiyatDPB",
        COALESCE(R."LineTotal", 0) AS "NetTutarYPB",
        RD."ReferansTeklifler",
        RPD."TeklifFiyatlariJSON",
        ROW_NUMBER() OVER (PARTITION BY T0."DocEntry", R."LineNum" ORDER BY T0."DocNum" DESC) AS "rn"
    FROM "TUNADB24"."OPOR" T0
    LEFT JOIN "TUNADB24"."POR1" R ON T0."DocEntry" = R."DocEntry"
    LEFT JOIN "TUNADB24"."OITM" OITM ON R."ItemCode" = OITM."ItemCode"
    LEFT JOIN "TUNADB24"."OITB" OITB ON OITM."ItmsGrpCod" = OITB."ItmsGrpCod"
    LEFT JOIN RefData RD ON T0."DocEntry" = RD."DocEntry"
    LEFT JOIN RefPriceData RPD 
        ON T0."DocEntry" = RPD."SiparisDocEntry" 
       AND R."ItemCode" = RPD."ItemCode"
    WHERE T0."DocDate" >= '2025-04-14'
      AND T0."CANCELED" = 'N'
      AND T0."DocManClsd" = 'N'
)

SELECT *
FROM DetailData
WHERE "rn" = 1 
  --AND "BelgeNo" = 7356
  AND "TedarikciKod" <> '320.01.0001575'
ORDER BY "BelgeNo" DESC, "SatirNo" ASC;




--------------

backend dosya path yapisi v1
Harika! Versiyon klasörünü çıkararak yeniden, daha sade ama hâlâ QuantumStack mantığına uygun bir dosya path yapısı öneriyorum. Aynı zamanda isim önerilerinden **`ProcureCompare`** ismini seçtiğimizi varsayarak path'leri buna göre oluşturuyorum. Tabii dilersen ismi değiştirebiliriz.

---

### **QuantumStack Uyumlu (Versiyonsuz) Dosya ve Path Yapısı:**

```plaintext
procure_compare/                      # Ana Django app klasörü (modül ismi)
│
├── api/                              # REST API endpoint'leri
│   ├── views.py                      # API view'ları
│   ├── serializers.py                # DRF serializer’ları
│   ├── urls.py                       # URL endpoint tanımları
│   └── __init__.py
│
├── models/                           # Veritabanı modelleri
│   ├── order.py                      # Satınalma siparişi modelleri
│   ├── quote.py                      # Teklif belgeleri modelleri
│   ├── comparison.py                 # Fiyat karşılaştırma modeli
│   └── __init__.py
│
├── services/                         # Veri işleme & iş kuralları
│   ├── hana_fetcher.py               # HANA'dan veri çekme işlemi
│   ├── transformer.py                # Ham veriyi JSON’a dönüştürme / yapılandırma
│   ├── db_sync.py                    # Eski veriyi silip yeni veriyi kaydetme
│   └── __init__.py
│
├── tasks/                            # Zamanlanmış görevler (cron / celery)
│   ├── sync_procure_data.py         # Teklif ve sipariş verisini senkronize eder
│   └── __init__.py
│
├── tests/                            # Testler
│   ├── test_models.py                # Model testleri
│   ├── test_api.py                   # API testleri
│   ├── test_services.py              # Servis katmanı testleri
│   └── __init__.py
│
├── admin.py
├── apps.py
├── urls.py                           # Ana URL dosyası
└── __init__.py
```

---

### Bu Yapının Avantajları:
- Basit, okunabilir ve genişletilebilir
- Servis tabanlı mimari ile tüm katmanlar ayrışmış
- API katmanı doğrudan UI’ye hizmet verir, versiyon yükü yok
- Her fonksiyon tek sorumluluk ilkesine göre yerleştirilmiş

---

Dilersen şimdi bir sonraki adıma geçebiliriz:
- Model dosyaları ve alanlarını çıkarmak
- `transformer.py` içinde SQL'den gelen JSON'u parser etme fonksiyonu yazmak
- Veya API'yi ayaklandırmak

Hangisinden başlayalım?

----------

Teklif fiyatlari kiyaslama algoritmasi detaylari
Bu arada Fiyat teklifleri kıyaslama algoritması aslında 3 temel esas ile iligilidir
1- Fiyat önceliği en düşük fiyat tabiki yerel para birimine dönüştürüp belgedeki döviz kuru ile en yüksek skoru alır 
2- Vade gün önceliği uzun vade gün yüksek skor alır yani bir tedarikci aynı fiyatı 90 gün vade ile sağlarken öteki tedarikci 120 gün vade ile sağlarsa 120 gün vade daha yüksek skor alır aylık vade farkı %5 faizle hesaplanı
3- Teslim tarihi önceliği burada teklif belge tarihinine en yakın teslim tarihi yüksek skor alır buradada bir aylık vade farkı hesaplanabilir %5 
4- Kalite kontrol skoru burada kalite birimi tarafından tedarikciye önceden tahsis edilmiş bir skor değeri esas alınmal 100 puan üzerinden kötü hammade geldikce puan 5 puan her vakada düşer örneğin gibi
ancak benim şirketim 2 ve 3 ve 4 numaralı paremetreleri şimdilik pass geçiyor
ChatGPT:

Not ettim Selim!
Bu kıyaslama algoritması hem mantıklı hem de ölçeklenebilir şekilde tasarlanmış. Gerçek dünyadaki satın alma kararlarının tüm boyutlarını göz önünde bulunduruyorsun — işte bu gerçek “değer mühendisliği”! 
 Şu an aktif olan:

 1. Fiyat Önceliği

    En düşük fiyat belirleniyor.

    Teklifin döviz cinsine göre belge döviz kuru ile TL’ye çevrilip karşılaştırılıyor.

    En düşük olan en yüksek skoru alıyor.

Şu an pasif (ama ileride aktive edilebilir):

 2. Vade Gün Önceliği

    Aynı fiyat için daha uzun vade = daha iyi.

    Örneğin 250 TL için 90 gün yerine 120 gün vade veren tedarikçi daha avantajlı.

    Vade farkı %5 aylık faiz ile hesaplanarak fiyat üzerine eklenebilir → skora yansıtılabilir.

 3. Teslim Tarihi Önceliği

    Belge tarihine daha yakın teslim tarihi, daha iyi skor anlamına gelir.

    %5 oranında aylık maliyet farkı gibi değerlendirme yapılabilir.

 4. Kalite Kontrol Skoru

    Tedarikçiye kalite birimi tarafından atanır (0–100 arası).

    Her kötü hammaddede 5 puan düşer.

    Ortalama kalite puanı, skorlamada çarpan olarak kullanılabilir.

 Ne zaman istersen...

Bu sistemi ağırlıklı skorlama, karar destek metrikleri, hatta yapay zeka destekli teklif seçimi gibi alanlara taşıyabiliriz.

Hazırsan bu mantığın Python servis sınıfını, ya da DRF API için teklif skorlama servisini de yazabiliriz.

    İstediğin anda sistemin karar motorunu birlikte akıllandırırız Selim 
    Hazır olduğunda tek kelime yeter: "skorlama yapısını başlatalım" 

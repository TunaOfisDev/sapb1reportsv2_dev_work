Anladım, Decimal veri türünün JSON seri hale getirilemediği bir hatayla karşılaşıyorsunuz. Bu, genellikle Python'da JSON'a dönüştürülmeye çalışırken karşılaşılan bir sorundur. Decimal veri türü, JSON'a dönüştürülürken doğrudan desteklenmez.

Bu sorunu çözmek için JSON'a dönüştürmeden önce Decimal veri türünü başka bir veri türüne çevirmeniz gerekebilir. İşte bu sorunu çözmek için birkaç adım:

1. Decimal verileri Float veya String olarak çevirin:
   SQL sorgunuzdaki Decimal alanını JSON'a dönüştürmeden önce Float veya String veri türüne çevirebilirsiniz. Örneğin:

   ```sql
   SELECT 
       O."DocEntry", 
       O."CardCode",   
       O."CardName" ,
       CAST(O."DocTotal" AS FLOAT) AS "DocTotal"
   FROM "TUNATEST"."ORDR" O
   WHERE O."DocDate" >= '01.01.2023'
   ```

   veya

   ```sql
   SELECT 
       O."DocEntry", 
       O."CardCode",   
       O."CardName" ,
       O."DocTotal"
   FROM "TUNATEST"."ORDR" O
   WHERE O."DocDate" >= '01.01.2023'
   ```

   Bu, Decimal verilerin JSON'a dönüştürülebilir bir formata getirilmesini sağlar.

2. Dönüştürülmüş verileri JSON olarak döndürün:
   Sorgunuzu bu şekilde düzenledikten sonra, veriler JSON formatına çevrilebilir ve döndürülebilir. Ancak, bu dönüşümü hangi dil veya araçla yapıyorsanız, ilgili dil veya araç kullanımına uygun bir şekilde yapmalısınız. Örneğin, Python kullanıyorsanız, `json.dumps` fonksiyonunu kullanarak JSON'a dönüştürebilirsiniz.

   Python örneği:

   ```python
   import json

   # Decimal verileri Float veya String olarak çevirdikten sonra alın
   result = [
       [93, "120010002", "AKBANK TÜRK ANONİM ŞİRKETİ", float(1000.50)],
       [19, "120010002", "AKBANK TÜRK ANONİM ŞİRKETİ", float(750.25)]
       # Diğer veriler
   ]

   # JSON'a dönüştür
   json_result = json.dumps(result)
   ```

Bu şekilde, Decimal verilerinizi uygun bir veri türüne dönüştürdükten sonra JSON formatına çevirebilirsiniz.

SELECT 
    O."DocEntry", 
    O."DocNum", 
    O."DocType", 
    O."CANCELED", 
    O."DocStatus", 
    O."DocDate",
    O."CardCode", 
    O."CardName", 
    O."VatPercent",
    O."VatSum" ,
    O."DiscPrcnt" ,
    O."DiscSum" ,
    O."DiscSumFC", 
    O."DocCur", 
    O."DocTotal" ,
    O."DocTotalFC",
    O."SlpCode", 
    O."CurSource"
    
FROM "TUNATEST"."ORDR" O

WHERE O."DocDate" >= '01.01.2023'


kalem listesi grup bazında

SELECT
    I."ItemCode",
    I."ItemName",
    I."ItmsGrpCod",
    IG."ItmsGrpNam"
FROM "TUNATEST"."OITM" I
LEFT JOIN "TUNATEST"."OITB" IG ON I."ItmsGrpCod" = IG."ItmsGrpCod"


**********

OITM KOLON ADLARI LİSTİ STOK KART

SELECT COLUMN_NAME
            FROM SYS.TABLE_COLUMNS
            WHERE SCHEMA_NAME = 'TUNATEST'
            AND TABLE_NAME = 'OITM'
            ORDER BY POSITION

****
kalem resimleri listesi

SELECT
    I."ItemCode",
    I."ItemName",
    I."ItmsGrpCod",
    IG."ItmsGrpNam",
    I."PicturName"
FROM "TUNATEST"."OITM" I
LEFT JOIN "TUNATEST"."OITB" IG ON I."ItmsGrpCod" = IG."ItmsGrpCod"
WHERE I."PicturName" != '?'


SELECT
    I."ItemCode",
    I."ItemName",
    I."ItmsGrpCod",
    IG."ItmsGrpNam"
FROM "TUNATEST"."OITM" I
LEFT JOIN "TUNATEST"."OITB" IG ON I."ItmsGrpCod" = IG."ItmsGrpCod"



*********

WITH RiskCalculation AS (
    SELECT 
        OCRD."CardCode",
        OCRD."CardName",
        COALESCE((SELECT SUM(JDT1."Debit") - SUM(JDT1."Credit") 
                  FROM "TUNATEST"."JDT1" AS JDT1
                  WHERE JDT1."ShortName" = OCRD."CardCode"
        ), 0) AS "Balance",
        COALESCE((SELECT SUM(ORDR."DocTotal")
                  FROM "TUNATEST"."ORDR" AS ORDR
                  WHERE ORDR."CardCode" = OCRD."CardCode"
                  AND ORDR."DocStatus" = 'O'
                  ), 0) AS "TotalOrders",
        COALESCE((SELECT SUM(ODLN."DocTotal")
                  FROM "TUNATEST"."ODLN" AS ODLN
                  WHERE ODLN."CardCode" = OCRD."CardCode"
                  AND ODLN."DocStatus" = 'O'
                 ), 0) AS "TotalDelivery"
    FROM "TUNATEST"."OCRD" AS OCRD
)
SELECT
    "CardCode",
    "CardName",
    "Balance",
    "TotalOrders",
    "TotalDelivery",
    ("Balance" + "TotalOrders" + "TotalDelivery") AS "TotalRisk"
FROM
    RiskCalculation
WHERE
    ("Balance" + "TotalOrders" + "TotalDelivery") != 0;



*********


*** paremteli sql sorgu test 
http://127.0.0.1:8000/api/v2/hanadbcon/query/TEST/?startdate=2023-01-01&enddate=2023-12-31

***********************
*** totalrisk sql name
WITH RiskCalculation AS (
        SELECT 
            "CardCode",
            "CardName",
            COALESCE((SELECT SUM("Debit") - SUM("Credit") 
                    FROM "TUNATEST"."JDT1" 
                    WHERE "ShortName" = "TUNATEST"."OCRD"."CardCode"
                    AND "RefDate" BETWEEN ? AND ?), 0) AS "Balance",
            COALESCE((SELECT SUM("DocTotal")
                    FROM "TUNATEST"."ORDR"
                    WHERE "CardCode" = "TUNATEST"."OCRD"."CardCode"
                    AND "DocStatus" = 'O'
                    AND "DocDate" BETWEEN ? AND ?), 0) AS "TotalOrders",
            COALESCE((SELECT SUM("DocTotal")
                    FROM "TUNATEST"."ODLN"
                    WHERE "CardCode" = "TUNATEST"."OCRD"."CardCode"
                    AND "DocStatus" = 'O'
                    AND "DocDate" BETWEEN ? AND ? ), 0) AS "TotalDelivery"
        FROM "TUNATEST"."OCRD"
    )
    SELECT
        "CardCode",
        "CardName",
        "Balance",
        "TotalOrders",
        "TotalDelivery",
        ("Balance" + "TotalOrders" + "TotalDelivery") AS "TotalRisk"
    FROM
        RiskCalculation
    WHERE
        ("Balance" + "TotalOrders" + "TotalDelivery") != 0;

*****************


http://127.0.0.1:8000/api/v2/hanadbcon/query/totalriskbalance/?startdate=2023-01-01&enddate=2023-12-31

[
    {
        "name": "startdate",
        "type": "date",
        "description": "Başlangıç tarihi"
    },
    {
        "name": "enddate",
        "type": "date",
        "description": "Bitiş tarihi"
    }
 
   
]
****************

http://127.0.0.1:8000/api/v2/hanadbcon/query/productpicture/
productpicture
****
SELECT I."ItemCode", COALESCE(I."ItemName", 'Tanımsız') AS "ItemName", 
IG."ItmsGrpNam", COALESCE(I."PicturName", 'Boş') AS "PicturName", 
I."UpdateDate" FROM "{schema}"."OITM" I LEFT JOIN "{schema}"."OITB" IG ON I."ItmsGrpCod" = IG."ItmsGrpCod"
WHERE I."U_EskiKod" IS NULL AND I."ItmsGrpCod" IN (105,112)



productpicture  fiyat+doviztip
SELECT 
    I."ItemCode", 
    COALESCE(I."ItemName", 'Tanımsız') AS "ItemName", 
    IG."ItmsGrpNam", 
    COALESCE(I."PicturName", 'Boş') AS "PicturName", 
    I."UpdateDate",
    ITM1."Price",
    ITM1."Currency"
FROM 
    "{schema}"."OITM" I 
LEFT JOIN 
    "{schema}"."OITB" IG ON I."ItmsGrpCod" = IG."ItmsGrpCod"
LEFT JOIN 
    "{schema}"."ITM1" ITM1 ON I."ItemCode" = ITM1."ItemCode" AND ITM1."PriceList" = 1
WHERE 
    I."U_EskiKod" IS NULL AND 
    I."ItmsGrpCod" IN (105, 112);


    SELECT 
    I."ItemCode", 
    COALESCE(I."ItemName", 'Tanımsız') AS "ItemName", 
    IG."ItmsGrpNam", 
    COALESCE(I."PicturName", 'Boş') AS "PicturName", 
    I."UpdateDate",
    ITM1."Price",
    ITM1."Currency"
FROM 
    "{schema}"."OITM" I 
LEFT JOIN 
    "{schema}"."OITB" IG ON I."ItmsGrpCod" = IG."ItmsGrpCod"
LEFT JOIN 
    "{schema}"."ITM1" ITM1 ON I."ItemCode" = ITM1."ItemCode" AND ITM1."PriceList" = 1
WHERE 
    I."ItemCode" IS NOT NULL AND
    I."U_EskiKod" IS NULL AND 
    I."ItmsGrpCod" IN (105, 112);


*****
totalrisk sql sorgu 02022024

SELECT
O."CardCode"   AS "MuhatapKod",
O."ChannlBP"   AS "AvansKod",
O."CardName"   AS "MuhatapAd",
O."Balance"    AS "Bakiye",
O."DNotesBal"  AS "AcikTeslimat",
O."OrdersBal"  AS "AcikSiparis",
(O."Balance" + O."DNotesBal" + O."OrdersBal") AS "ToplamRisk"

FROM "TUNADB24".OCRD O

WHERE (O."Balance" + O."DNotesBal" + O."OrdersBal") != 0

ORDER BY "ToplamRisk" desc
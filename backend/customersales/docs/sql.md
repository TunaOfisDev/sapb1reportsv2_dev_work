-- Rapor Seti: Müşteri Bazlı Net Satış (SPB/EUR) – OWDD Son Adım Onaylı (Status='Y')
WITH LastStep AS (   -- Her belge için son adım (en büyük WddCode)
    SELECT
        W."DocEntry",
        MAX(W."WddCode") AS "LastWddCode"
    FROM "TUNADB24"."OWDD" W
    WHERE W."ObjType" = '17'  -- Sales Order
    GROUP BY W."DocEntry"
),
ApprovedDocs AS (    -- Yalnızca son adımı 'Y' olan belgeler
    SELECT W."DocEntry"
    FROM "TUNADB24"."OWDD" W
    JOIN LastStep L
      ON L."DocEntry" = W."DocEntry"
     AND L."LastWddCode" = W."WddCode"
    WHERE COALESCE(W."Status",'N') = 'Y'
),
BaseLines AS (       -- Ortak veri kümesi
    SELECT
        T."DocEntry",
        R."LineNum",
        ROW_NUMBER() OVER (PARTITION BY T."DocEntry", R."LineNum" ORDER BY T."DocNum" DESC) AS "rn",
        T."TaxDate",
        T."CardCode",
        C."CardName",
        CAST(T."U_sales_type" AS NVARCHAR(50)) AS "SatisTipi",
        COALESCE(S."SlpName", 'Tanımsız') AS "Satici",
        OCRG."GroupName" AS "CariGrup",
        R."TotalSumSy" AS "NetTutarSPB",   -- EUR (Sistem PB)
        R."LineTotal"  AS "NetTutarYPB"    -- TL  (Yerel PB)
    FROM "TUNADB24"."ORDR" T
    JOIN "TUNADB24"."RDR1" R       ON T."DocEntry" = R."DocEntry"
    JOIN "TUNADB24"."OCRD" C       ON T."CardCode" = C."CardCode"
    LEFT JOIN "TUNADB24"."OSLP" S  ON C."SlpCode"  = S."SlpCode"
    LEFT JOIN "TUNADB24"."OCRG" OCRG ON C."GroupCode" = OCRG."GroupCode"
    JOIN ApprovedDocs A            ON A."DocEntry" = T."DocEntry"   -- 🔒 sadece OWDD son adımı Y
    WHERE
        YEAR(T."TaxDate") = YEAR(CURRENT_DATE)
        AND (T."CANCELED"   IS NULL OR T."CANCELED"   = 'N')
        AND (T."DocManClsd" IS NULL OR T."DocManClsd" = 'N')
        AND CAST(T."U_sales_type" AS NVARCHAR(50)) <> 'IPTAL'
        AND T."CardCode" NOT IN (
            '120.02.0000013', '120.90.0000075', '393.01.0000001', '120.99.0000083',
            '120.01.0001241', '120.01.0001278', '120.90.0000760', '393.12.0000001'
        )
),
Lines AS (
    SELECT * FROM BaseLines WHERE "rn" = 1
),

-- 1) Aylık Pivot (SPB/EUR)
CTE_Pivot AS (
    SELECT
       
        "Satici",
        "SatisTipi",
        "CariGrup",
        "CardCode" AS "MusteriKodu",
        "CardName" AS "MusteriAdi",
        YEAR("TaxDate")  AS "Yil",
        MONTH("TaxDate") AS "Ay",
        SUM("NetTutarSPB") AS "AylikNetSPB"
    FROM Lines
    GROUP BY
        "CariGrup","Satici","SatisTipi","CardCode","CardName",
        YEAR("TaxDate"), MONTH("TaxDate")
)
SELECT
    
    P."Satici",
    P."SatisTipi",
    P."CariGrup",
    P."MusteriKodu",
    P."MusteriAdi",
    SUM(P."AylikNetSPB") AS "ToplamNetSPB_EUR",
    COALESCE(MAX(CASE WHEN P."Ay" = 1  THEN P."AylikNetSPB" END), 0) AS "Ocak",
    COALESCE(MAX(CASE WHEN P."Ay" = 2  THEN P."AylikNetSPB" END), 0) AS "Şubat",
    COALESCE(MAX(CASE WHEN P."Ay" = 3  THEN P."AylikNetSPB" END), 0) AS "Mart",
    COALESCE(MAX(CASE WHEN P."Ay" = 4  THEN P."AylikNetSPB" END), 0) AS "Nisan",
    COALESCE(MAX(CASE WHEN P."Ay" = 5  THEN P."AylikNetSPB" END), 0) AS "Mayıs",
    COALESCE(MAX(CASE WHEN P."Ay" = 6  THEN P."AylikNetSPB" END), 0) AS "Haziran",
    COALESCE(MAX(CASE WHEN P."Ay" = 7  THEN P."AylikNetSPB" END), 0) AS "Temmuz",
    COALESCE(MAX(CASE WHEN P."Ay" = 8  THEN P."AylikNetSPB" END), 0) AS "Ağustos",
    COALESCE(MAX(CASE WHEN P."Ay" = 9  THEN P."AylikNetSPB" END), 0) AS "Eylül",
    COALESCE(MAX(CASE WHEN P."Ay" = 10 THEN P."AylikNetSPB" END), 0) AS "Ekim",
    COALESCE(MAX(CASE WHEN P."Ay" = 11 THEN P."AylikNetSPB" END), 0) AS "Kasım",
    COALESCE(MAX(CASE WHEN P."Ay" = 12 THEN P."AylikNetSPB" END), 0) AS "Aralık"
FROM CTE_Pivot P
GROUP BY
    P."CariGrup", P."Satici", P."SatisTipi", P."MusteriKodu", P."MusteriAdi"
HAVING
    SUM(P."AylikNetSPB") > 0
ORDER BY
    "ToplamNetSPB_EUR" DESC;

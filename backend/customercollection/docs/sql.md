customercollection


WITH Hesaplar AS (
    SELECT 
        "CardCode" AS "CARI_KOD", 
        "CardName" AS "CARI_AD",
        COALESCE("ChannlBP", "CardCode") AS "AVANSHESAPKOD",
        "GroupNum" AS "ODEMEKOD" -- Ödeme kodunu OCRD tablosundan al
    FROM 
        "TUNADB24"."OCRD"
    WHERE 
        "CardCode" LIKE '120%'
),
CariHareketler AS (
    SELECT 
        J0."ShortName" AS "HESAP_KODU",
        O."CardName" AS "HESAP_AD",
        CASE 
            WHEN J1."TransCode" = 'ACF' AND J1."RefDate" = '2024-01-01' THEN '2023-12-31'
            ELSE TO_VARCHAR(J1."RefDate", 'YYYY-MM-DD') 
        END AS "BELGE_TARIH", 
        J1."TransId" || J0."Line_ID" AS "BELGE_NO", 
        TO_VARCHAR(J1."DueDate", 'YYYY-MM-DD') AS "VADE_TARIH",
        J0."Debit" AS "BORC",
        J0."Credit" AS "ALACAK",
        (J0."Debit" - J0."Credit") AS "BAKIYE"
    FROM 
        "TUNADB24"."JDT1" J0
        INNER JOIN "TUNADB24"."OJDT" J1 ON J0."TransId" = J1."TransId"
        INNER JOIN "TUNADB24"."OCRD" O ON J0."ShortName" = O."CardCode"
    WHERE 
        J0."ShortName" LIKE '120%'
),
KumulatifBakiye AS (
    SELECT 
        H."CARI_KOD",
        H."CARI_AD",
        CH."BELGE_TARIH",
        CH."VADE_TARIH",
        CH."BELGE_NO",
        H."ODEMEKOD",
        O0."PymntGroup" AS "ODEMEKOSULU",
        CH."BORC",
        CH."ALACAK",
        SUM(CH."BAKIYE") OVER (PARTITION BY H."CARI_KOD") AS "BAKIYE"
    FROM 
        CariHareketler CH
        LEFT JOIN Hesaplar H ON CH."HESAP_KODU" = H."CARI_KOD" OR CH."HESAP_KODU" = H."AVANSHESAPKOD"
        LEFT JOIN "TUNADB24"."OCTG" O0 ON H."ODEMEKOD" = O0."GroupNum"
)
SELECT *
FROM KumulatifBakiye
WHERE "BAKIYE" > 100
ORDER BY 
    "CARI_KOD", "BELGE_TARIH";

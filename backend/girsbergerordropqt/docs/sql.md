girsbergerordropqt

***
WITH DetailData AS (
    SELECT
        ROW_NUMBER() OVER (PARTITION BY T."DocEntry" || R."LineNum" ORDER BY T."DocNum" DESC) AS rn,
        T."DocEntry" || R."LineNum" AS "UniqDetailNo",
        T."DocNum"  AS "BelgeNo",
        S."SlpName" AS "Satici",
        TO_CHAR(T."TaxDate", 'YYYY-MM-DD') AS "BelgeTarih",
        TO_CHAR(T."DocDueDate", 'YYYY-MM-DD') AS "TeslimTarih",
        T."WddStatus" AS "BelgeOnay",
        CASE WHEN T."DocStatus" = 'O' THEN 'Açık' ELSE 'Kapalı' END AS "BelgeStatus",
        COALESCE(T."Address2",'Yok') AS "SevkAdres",
        T."CardCode" AS "MusteriKod",
        T."CardName" AS "MusteriAd",
        T."U_sales_type" AS "SatisTipi",
        OITB."ItmsGrpCod" AS "KalemGrupKod",
        OITB."ItmsGrpNam" AS "KalemGrup",
        CASE WHEN R."LineStatus" = 'O' THEN 'Açık' ELSE 'Kapalı' END AS "SatirStatus",
        R."ItemCode" AS "KalemKod",
        R."Dscription" AS "KalemTanimi",
        R."UomCode" AS "Birim",
        COALESCE(R."Quantity", 0) AS "SipMiktar",
        COALESCE(R."DelivrdQty", 0) AS "SevkMiktar",
        COALESCE(R."OpenCreQty", 0) AS "KalanMiktar",
        COALESCE(R."PriceBefDi", 0) AS "ListeFiyatDPB",
        CASE WHEN R."Currency" = 'TRY' THEN 1 ELSE COALESCE(R."Rate", 1) END AS "DetayKur",
        COALESCE(R."Currency", 'TRY') AS "DetayDoviz",
        COALESCE(R."DiscPrcnt", 0) AS "IskontoOran",
        COALESCE(R."Price", 0) AS "NetFiyatDPB",
        COALESCE(R."LineTotal", 0) AS "NetTutarYPB",
        COALESCE(((R."LineTotal" / NULLIF(R."Quantity", 0)) * R."OpenCreQty"), 0) AS "AcikNetTutarYPB",
        CASE WHEN OITB."ItmsGrpCod" = '112' THEN COALESCE(((R."LineTotal" / NULLIF(R."Quantity", 0)) * R."OpenCreQty"), 0) ELSE 0 END AS "GirsbergerNetTutarYPB",
        --Satinalma Teklif alanlari
        COALESCE(P."CardCode", 'Yok') AS "SalmaTeklifTedarikciKod",
        COALESCE(P."CardName", 'Yok') AS "SalmaTeklifTedarikciAd",
        COALESCE(P."DocNum", '0') AS "SalmaTeklifNo",
        COALESCE(Q."U_srcdocline", '0') AS "SalmaTeklifKaynakDetayNo",
        COALESCE(Q."ItemCode", 'Yok') AS "SalmaTeklifKalemNo",
        COALESCE(Q."Quantity", 0)   AS "SalmaTeklifMiktar",
        COALESCE(Q."DelivrdQty", 0)  AS "SalmaTeklifSevk",
        COALESCE(Q."OpenCreQty", 0) AS "SalmaTeklifKalanMiktar"

    FROM "TUNADB24"."ORDR" T
    LEFT JOIN "TUNADB24"."OPQT" P ON T."DocNum" = P."U_Satissipno"
    LEFT JOIN "TUNADB24"."RDR1" R ON T."DocEntry" = R."DocEntry"
    LEFT JOIN "TUNADB24"."PQT1" Q ON R."DocEntry" || R."LineNum" = Q."U_srcdocline"
    LEFT JOIN "TUNADB24"."OSLP" S ON T."SlpCode" = S."SlpCode"
    LEFT JOIN "TUNADB24"."OITM" OITM ON R."ItemCode" = OITM."ItemCode"
    LEFT JOIN "TUNADB24"."OITB" OITB ON OITB."ItmsGrpCod" = OITM."ItmsGrpCod"
    WHERE T."TaxDate" >= '2024-04-22' AND T."CANCELED" = 'N' AND T."DocManClsd" = 'N' AND OITB."ItmsGrpCod" = '112' --AND T."DocNum" = '2275'
)
SELECT *
FROM DetailData
WHERE rn = 1 
ORDER BY "BelgeNo" DESC;
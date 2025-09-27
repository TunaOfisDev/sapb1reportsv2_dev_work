salesofferdocsum

**
WITH DetailData AS (
    SELECT
        T."DocEntry" || '-' || R."LineNum" || '-' || ROW_NUMBER() OVER (PARTITION BY T."DocEntry", R."LineNum" ORDER BY T."DocNum" DESC) AS "UniqDetailNo",
        T."DocNum"  AS "BelgeNo",
        S."SlpName" AS "Satici",
        TO_CHAR(T."TaxDate", 'YYYY-MM-DD') AS "BelgeTarih",
        TO_CHAR(T."DocDueDate", 'YYYY-MM-DD') AS "TeslimTarih",
        T."WddStatus" AS "BelgeOnay",
        CASE WHEN T."DocStatus" = 'O' THEN 'Açık' ELSE 'Kapalı' END AS "BelgeStatus",
        T."Comments" AS "BelgeAciklamasi",
        T."Address2" AS "SevkAdres",
        T."CardCode" AS "MusteriKod",
        T."CardName" AS "MusteriAd",
        T."U_sales_type" AS "SatisTipi",
        OITB."ItmsGrpNam" AS "KalemGrup",
        CASE WHEN R."LineStatus" = 'O' THEN 'Açık' ELSE 'Kapalı' END AS "SatirStatus",
        R."LineNum" AS "SatirNo",
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
        COALESCE(R."OpenSumSys", 0) AS "NetTutarSPB",
        COALESCE(((R."LineTotal" / NULLIF(R."Quantity", 0)) * R."OpenCreQty"), 0) AS "AcikNetTutarYPB",
        COALESCE(((R."OpenSumSys"/NULLIF(R."Quantity", 0))*R."OpenCreQty"), 0) AS "AcikNetTutarSPB",
        ROW_NUMBER() OVER (PARTITION BY T."DocEntry", R."LineNum" ORDER BY T."DocNum" DESC) AS "rn"
    FROM "TUNADB24"."OQUT" T
    LEFT JOIN "TUNADB24"."QUT1" R ON T."DocEntry" = R."DocEntry"
    LEFT JOIN "TUNADB24"."OSLP" S ON T."SlpCode" = S."SlpCode"
    LEFT JOIN "TUNADB24"."OWDD" OWDD ON T."DocEntry" = OWDD."DocEntry"
    LEFT JOIN "TUNADB24"."OITM" OITM ON R."ItemCode" = OITM."ItemCode"
    LEFT JOIN "TUNADB24"."OITB" OITB ON OITB."ItmsGrpCod" = OITM."ItmsGrpCod"
    WHERE T."TaxDate" >= '2023-01-01' AND T."CANCELED" = 'N' AND T."DocManClsd" = 'N'
)
SELECT *
FROM DetailData
WHERE "rn" = 1 AND "BelgeOnay" != 'N'  AND "BelgeNo" = '6'
ORDER BY "BelgeNo" DESC, "SatirNo" ASC;

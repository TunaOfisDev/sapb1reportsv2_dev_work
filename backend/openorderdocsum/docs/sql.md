openorderdocsum

**
WITH DetailData AS (
    SELECT
        ROW_NUMBER() OVER (PARTITION BY T."DocEntry" || R."LineNum" ORDER BY T."DocNum" DESC) AS rn,
        T."DocEntry" || R."LineNum" AS "UniqDetailNo",
        T."DocNum"  AS "BelgeNo",
        S."SlpName" AS "Satici",
        TO_VARCHAR(T."TaxDate", 'DD.MM.YYYY') AS "BelgeTarih",
        TO_VARCHAR(T."DocDueDate", 'DD.MM.YYYY') AS "TeslimTarih",
        T."WddStatus" AS "BelgeOnay",
        CASE WHEN T."DocStatus" = 'O' THEN 'Açık' ELSE 'Kapalı' END AS "BelgeStatus",
        T."CardCode" AS "MusteriKod",
        T."CardName" AS "MusteriAd",
        T."U_sales_type" AS "SatisTipi",
        OITB."ItmsGrpNam" AS "KalemGrup",
        CASE WHEN R."LineStatus" = 'O' THEN 'Açık' ELSE 'Kapalı' END AS "SatirStatus",
        R."ItemCode" AS "KalemKod",
        R."Dscription" AS "KalemTanimi",
        R."UomCode" AS "Birim",
        R."Quantity" AS "SipMiktar",
        R."DelivrdQty" AS "SevkMiktar",
        R."OpenCreQty" AS "KalanMiktar",
        R."PriceBefDi" AS "ListeFiyatDPB",
        CASE WHEN R."Currency" = 'TRY' THEN 1 ELSE R."Rate" END AS "DetayKur",
        R."Currency" AS "DetayDoviz",
        R."DiscPrcnt" AS "IskontoOran",
        R."Price" AS "NetFiyatDPB",
        R."LineTotal" AS "NetTutarYPB",
        ((R."LineTotal" / R."Quantity") * R."OpenCreQty") AS "AcikNetTutarYPB",
        ((R."OpenSumSys"/R."Quantity")*R."OpenCreQty") AS  "AcikNetTutarSPB",
        CASE WHEN OITB."ItmsGrpCod" = '112' THEN ((R."LineTotal" / R."Quantity") * R."OpenCreQty") ELSE 0 END AS "GirsbergerNetTutarYPB",
        CASE WHEN OITB."ItmsGrpCod" = '105' THEN ((R."LineTotal" / R."Quantity") * R."OpenCreQty") ELSE 0 END AS "MamulNetTutarYPB",
        CASE WHEN OITB."ItmsGrpCod" NOT IN ('105', '112', '113') THEN ((R."LineTotal" / R."Quantity") * R."OpenCreQty") ELSE 0 END AS "TicariNetTutarYPB",
        CASE WHEN OITB."ItmsGrpCod" = 113 AND R."Dscription" LIKE '%NAKLİYE%' THEN ((R."LineTotal" / R."Quantity") * R."OpenCreQty") ELSE 0 END AS "NakliyeNetTutarYPB",
        CASE WHEN OITB."ItmsGrpCod" = 113 AND R."Dscription" LIKE '%MONTAJ%' THEN ((R."LineTotal" / R."Quantity") * R."OpenCreQty") ELSE 0 END AS "MontajNetTutarYPB"
    FROM "TUNADB24"."ORDR" T
    LEFT JOIN "TUNADB24"."RDR1" R ON T."DocEntry" = R."DocEntry"
    LEFT JOIN "TUNADB24"."OSLP" S ON T."SlpCode" = S."SlpCode"
    LEFT JOIN "TUNADB24"."OWDD" OWDD ON T."DocEntry" = OWDD."DocEntry"
    LEFT JOIN "TUNADB24"."OITM" OITM ON R."ItemCode" = OITM."ItemCode"
    LEFT JOIN "TUNADB24"."OITB" OITB ON OITB."ItmsGrpCod" = OITM."ItmsGrpCod"
    WHERE T."TaxDate" >= '2024-01-01' AND T."CANCELED" = 'N' AND T."DocManClsd" = 'N'   AND T."CardCode" = '120.90.0000107'
)
SELECT *
FROM DetailData
WHERE rn = 1
ORDER BY "BelgeNo" DESC;
WITH CTE_Orders AS (
    SELECT *, 'ORDR' AS "SourceTable" FROM "TUNADB24"."ORDR" 
    WHERE "ObjType" = '17'  AND "CANCELED" = 'N'
    UNION ALL
    SELECT *, 'ODRF' AS "SourceTable" FROM "TUNADB24"."ODRF" 
    WHERE "ObjType" = '17' AND "WddStatus" = 'W'  AND "CANCELED" = 'N'
),
CTE_Items AS (
    SELECT *, 'RDR1' AS "ItemSourceTable" FROM "TUNADB24"."RDR1"
    UNION ALL
    SELECT *, 'DRF1' AS "ItemSourceTable" FROM "TUNADB24"."DRF1"
),
CTE_LastApprovalStatus1 AS (
    SELECT
        "WddCode",
        "Status",
        ROW_NUMBER() OVER (PARTITION BY "WddCode" ORDER BY "UpdateDate" DESC, "UpdateTime" DESC) AS rn
    FROM
        "TUNADB24"."WDD1"
    WHERE
        "StepCode" = 1
),
CTE_LastApprovalStatus2 AS (
    SELECT
        "WddCode",
        "Status",
        ROW_NUMBER() OVER (PARTITION BY "WddCode" ORDER BY "UpdateDate" DESC, "UpdateTime" DESC) AS rn
    FROM
        "TUNADB24"."WDD1"
    WHERE
        "StepCode" = 2
)
SELECT
T."DocEntry" || T."DocNum" || R."LineNum" AS "unique_id",
    S."SlpName" AS "Satici",
    CASE WHEN T."SourceTable" = 'ORDR' THEN 'Satış Siparişi' ELSE 'Taslak' END AS "BelgeTur",
    LS1."Status" AS "Onay1Status",
    LS2."Status" AS "Onay2Status",
    TO_VARCHAR(T."TaxDate", 'DD.MM.YYYY') AS "BelgeTarihi",
    TO_VARCHAR(T."DocDueDate", 'DD.MM.YYYY') AS "TeslimTarihi",
    T."WddStatus" AS "BelgeOnay",
    CASE WHEN T."DocStatus" = 'O' THEN 'Açık' ELSE 'Kapalı' END AS "BelgeStatus",
    T."CardCode" AS "MusteriKod",
    T."CardName" AS "MusteriAd",
    T."DocEntry" AS "MasterBelgeGirisNo",
    CASE WHEN T."SourceTable" = 'ORDR' THEN T."DocNum" ELSE T."DocEntry" END AS "SipNo",
    T."U_sales_type" AS "SatisTipi",
    OITB."ItmsGrpNam" AS "KalemGrup",
    CASE WHEN R."LineStatus" = 'O' THEN 'Açık' ELSE 'Kapalı' END AS "SatirStatus",  
    R."DocEntry" AS "DetayBelgeGiris",
    R."LineNum" AS "SatirNo",
    R."WhsCode" AS "DepoKod",
    R."ItemCode" AS "KalemKod",
    R."Dscription" AS "KalemTanimi",
    R."UomCode" AS "Birim",
    R."Quantity" AS "SipMiktar",
    R."DelivrdQty" AS "SevkMiktar",
    R."OpenCreQty" AS "KalanMiktar",
    
    -- yabancı para birimi eur
    R."PriceBefDi" AS "ListeFiyatDPB",
    CASE WHEN R."Currency"= 'TRY' THEN 1 ELSE R."Rate" END AS "DetayKur",
    R."Currency" AS "DetayDoviz",
    R."DiscPrcnt"  AS "IskontoOran",
    R."Price"      AS "NetFiyatDPB",
    CAST((R."Quantity" * R."PriceBefDi") AS DECIMAL(18,4)) AS "BrutTutarDPB",
    CAST(CASE WHEN R."Currency" = 'TRY' THEN R."LineTotal" ELSE (R."LineTotal" / NULLIF(R."Rate", 0)) END AS DECIMAL(18,4)) AS "NetTutarDPB",
    CAST(CASE WHEN R."Currency" = 'TRY' THEN ((R."Quantity" * R."PriceBefDi") * (R."DiscPrcnt" / 100)) ELSE ((R."Quantity" * R."PriceBefDi") - (R."LineTotal" / NULLIF(R."Rate", 0))) END AS DECIMAL(18,2)) AS "IskTutarDPB",  
    CAST(CASE WHEN R."Currency" = 'TRY' THEN R."VatSum" ELSE (R."VatSum" / NULLIF(R."Rate", 0)) END AS DECIMAL(18,4)) AS "KdvTutarDPB",
    CAST(CASE WHEN R."Currency" = 'TRY' THEN (R."LineTotal"/NULLIF(T."DocRate", 0))+ ((R."LineTotal"/ NULLIF(T."DocRate", 0))*R."VatPrcnt")/100    ELSE R."GTotalSC" END AS DECIMAL(18,4)) AS "KdvliNetTutarDPB",
    CASE WHEN T."DocCur" = 'TRY' THEN 1 ELSE T."DocRate" END AS "BelgeKur",
    T."DocCur" AS "BelgeDoviz",
    
    -- Yerel para birimi cinsinden hesaplamalar
    CAST((R."Price" * (CASE WHEN T."DocRate" = 0 THEN 1 ELSE T."DocRate" END)) AS DECIMAL(18,4)) AS "ListeFiyatYPB",
    CAST((R."Quantity" * R."PriceBefDi" * COALESCE(NULLIF(R."Rate", 0), 1)) AS DECIMAL(18,4)) AS "BrutTutarYPB",
    CAST(((R."Quantity" * R."PriceBefDi" * COALESCE(NULLIF(R."Rate", 0), 1)) * (R."DiscPrcnt" / 100)) AS DECIMAL(18,2)) AS "IskTutarYPB",
    CAST((R."LineTotal" * COALESCE(NULLIF(R."Rate", 0), 1)) AS DECIMAL(18,4)) AS "NetTutarYPB",
    R."VatPrcnt" AS "KdvOran",
    R."VatGroup",
    R."VatSum" AS "KdvTutarYPB",  
    CAST((R."GTotal" * COALESCE(NULLIF(R."Rate", 0), 1)) AS DECIMAL(18,6)) AS "KdvliNetTutarYPB"
FROM
    CTE_Orders T
LEFT JOIN CTE_Items R ON T."DocEntry" = R."DocEntry" AND T."SourceTable" = CASE 
                                                                            WHEN R."ItemSourceTable" = 'RDR1' THEN 'ORDR'
                                                                            WHEN R."ItemSourceTable" = 'DRF1' THEN 'ODRF'
                                                                            END
LEFT JOIN "TUNADB24"."OSLP" S ON T."SlpCode" = S."SlpCode"
LEFT JOIN "TUNADB24"."OWDD" OWDD ON T."DocEntry" = OWDD."DocEntry"
LEFT JOIN "TUNADB24"."OITM" OITM ON R."ItemCode" = OITM."ItemCode"
LEFT JOIN "TUNADB24"."OITB" OITB ON OITB."ItmsGrpCod" = OITM."ItmsGrpCod"
LEFT JOIN CTE_LastApprovalStatus1 LS1 ON OWDD."WddCode" = LS1."WddCode" AND LS1.rn = 1
LEFT JOIN CTE_LastApprovalStatus2 LS2 ON OWDD."WddCode" = LS2."WddCode" AND LS2.rn = 1
WHERE --T."DocNum"= 1108 AND
      T."TaxDate" >= '2024-01-03' AND
    (OWDD."WddCode" IS NULL OR OWDD."WddCode" IN (
        SELECT MAX("WddCode")
        FROM "TUNADB24"."OWDD"
        WHERE "DocEntry" = T."DocEntry"
    )) 
ORDER BY R."LineNum" ASC

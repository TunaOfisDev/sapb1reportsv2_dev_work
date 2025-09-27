-- Hammade Depo Stok Durum
SELECT 
    T1."WhsCode" AS "DepoKod",
    T6."ItmsGrpNam" AS "KalemGrupAd",
    T0."InvntItem" AS "StokKalem",
    T0."SellItem" AS "SatisKalem",
    T0."PrchseItem" AS "SatinalmaKalem",
    T0."Phantom" AS "YapayKalem",
    T0."ItemCode" AS "KalemKod",
    T0."ItemName" AS "Kalemtanim",
    T3."UomCode" AS "StokOlcuBirim",
    COALESCE(T1."OnHand", 0) AS "DepoStok",
    COALESCE(T2."Quantity", 0) AS "SiparisEdilenMiktar",
    COALESCE(T4."LastPurPrc", 0) AS "SonSatınalmaFiyat",
    COALESCE(TO_VARCHAR(T4."DocDate", 'DD.MM.YYYY'), '01.01.1900') AS "SonSatinalmaFaturaTarih",
    COALESCE(T5."SiparisDetaylari", 'Yok') AS "VerilenSiparisler"
    
FROM 
    "TUNADB24"."OITM" T0
    LEFT JOIN "TUNADB24"."OITW" T1 ON T0."ItemCode" = T1."ItemCode" AND T1."WhsCode" = 'H-01'
    LEFT JOIN (
        SELECT "ItemCode", SUM("Quantity") AS "Quantity"
        FROM "TUNADB24"."POR1"
        WHERE "WhsCode" = 'H-01'
        GROUP BY "ItemCode"
    ) T2 ON T0."ItemCode" = T2."ItemCode"
    LEFT JOIN "TUNADB24"."OUOM" T3 ON T0."BuyUnitMsr" = T3."UomCode"
    LEFT JOIN (
        SELECT 
            T5."ItemCode", 
            T5."Price" * T6."DocRate" AS "LastPurPrc",
            T6."DocDate"
        FROM "TUNADB24"."PCH1" T5
        JOIN "TUNADB24"."OPCH" T6 ON T5."DocEntry" = T6."DocEntry"
        WHERE T6."DocDate" = (
            SELECT MAX(T6_sub."DocDate")
            FROM "TUNADB24"."OPCH" T6_sub
            JOIN "TUNADB24"."PCH1" T5_sub ON T6_sub."DocEntry" = T5_sub."DocEntry"
            WHERE T5_sub."ItemCode" = T5."ItemCode"
        )
    ) T4 ON T0."ItemCode" = T4."ItemCode"
    LEFT JOIN (
        SELECT 
            R."ItemCode",
            STRING_AGG(TO_VARCHAR(S."DocDate", 'DD.MM.YYYY') || '-' || LEFT(C."CardName", 20) || '-' || S."Comments", ', ') AS "SiparisDetaylari"
        FROM 
            "TUNADB24"."POR1" R
        JOIN 
            "TUNADB24"."OPOR" S ON R."DocEntry" = S."DocEntry"
        JOIN 
            "TUNADB24"."OCRD" C ON S."CardCode" = C."CardCode"
        WHERE 
            R."WhsCode" = 'H-01'
        GROUP BY 
            R."ItemCode"
    ) T5 ON T0."ItemCode" = T5."ItemCode"
    LEFT JOIN "TUNADB24"."OITB" T6 ON T0."ItmsGrpCod" = T6."ItmsGrpCod"

--WHERE 
   -- T0."ItmsGrpCod" = 106 
    --AND T0."ItemCode" = '92118480112'

GROUP BY
    T1."WhsCode", T6."ItmsGrpNam", T0."InvntItem",T0."SellItem",T0."PrchseItem",T0."Phantom", T0."ItemCode", T0."ItemName", T3."UomCode", T1."OnHand", T2."Quantity", T4."LastPurPrc", T4."DocDate", T5."SiparisDetaylari"
ORDER BY "KalemKod" ASC;
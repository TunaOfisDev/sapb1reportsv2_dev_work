SELECT 
    T0."ShortName" AS "CARI_KOD", 
    T2."CardName" AS "CARI_AD", 
    
    --CASE WHEN T1."TransCode" = 'ACF' AND T1."RefDate" = '2024-01-01' THEN '2023-12-31' ELSE TO_VARCHAR(T1."RefDate", 'YYYY-MM-DD') END AS "BELGE_TARIH",
    
    TO_VARCHAR(T1."RefDate", 'YYYY-MM-DD') AS "BELGE_TARIH",  
    
    T1."TransId" || T0."Line_ID" AS "BELGE_NO", 
   --TO_VARCHAR(T1."DueDate", 'YYYY-MM-DD') AS "VADE_TARIH",
    T2."IBAN" AS "IBAN",
    --T2."GroupNum" AS "ODEMEKOD",
    T3."PymntGroup" AS "ODEMEKOSULU",
    SUM(T0."Debit") AS "BORC", 
    SUM(T0."Credit") AS "ALACAK"
FROM 
    "TUNADB24"."JDT1" T0
    INNER JOIN "TUNADB24"."OJDT" T1 ON T0."TransId" = T1."TransId"
    LEFT JOIN "TUNADB24"."OCRD" T2 ON T0."ShortName" = T2."CardCode"
    LEFT JOIN "TUNADB24"."OCTG" T3 ON T2."GroupNum" = T3."GroupNum"
INNER JOIN (
    SELECT 
        "ShortName",
        SUM("Debit") - SUM("Credit") AS "Balance"
    FROM 
        "TUNADB24"."JDT1"
    GROUP BY 
        "ShortName"
) AS T4 ON T0."ShortName" = T4."ShortName" AND T4."Balance" < -100 -- Düzeltildi
WHERE 
    T0."ShortName" LIKE '320%' AND
    T0."ShortName" NOT IN ('320.01.0001755', '320.01.0001576')
GROUP BY 
    T0."ShortName", 
    T2."CardName", 
    T1."RefDate", 
    T1."TransId", 
    T0."Line_ID",
    T1."DueDate",
    T2."IBAN",
    T2."GroupNum",
    T3."PymntGroup",
    T1."TransCode" -- 'T1."TransCode"' alanı eklendi
HAVING 
    SUM(T0."BalDueDeb") - SUM(T0."BalDueCred") != 0
ORDER BY 
    "BELGE_TARIH" ASC;
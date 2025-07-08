deliverydocsumv2

*****

SELECT
    S."SlpName" AS "Temsilci",
    G."GroupName" AS "CariGrup",
    C."CardCode" AS "CariKod",
    C."CardName" AS "CariAdi",  
   
    SUM(CASE WHEN DAYS_BETWEEN(CURRENT_DATE, I."TaxDate") =  0 THEN L."LineTotal" ELSE 0 END) AS "Bugun",
    SUM(CASE WHEN DAYS_BETWEEN(CURRENT_DATE, I."TaxDate") = -1 THEN L."LineTotal" ELSE 0 END) AS "Bugun-1",
    SUM(CASE WHEN DAYS_BETWEEN(CURRENT_DATE, I."TaxDate") = -2 THEN L."LineTotal" ELSE 0 END) AS "Bugun-2",
    SUM(CASE WHEN DAYS_BETWEEN(CURRENT_DATE, I."TaxDate") = -3 THEN L."LineTotal" ELSE 0 END) AS "Bugun-3",
    SUM(CASE WHEN DAYS_BETWEEN(CURRENT_DATE, I."TaxDate") = -4 THEN L."LineTotal" ELSE 0 END) AS "Bugun-4",
    
    ---- son iki ay ayrı ayırı toplamlar
    SUM(CASE WHEN TO_CHAR(I."TaxDate", 'YYYYMM') = TO_CHAR(CURRENT_DATE, 'YYYYMM') THEN L."LineTotal" ELSE 0 END) AS "BuAyToplam",
    SUM(CASE WHEN TO_CHAR(I."TaxDate", 'YYYYMM') = TO_CHAR(ADD_MONTHS(CURRENT_DATE, -1), 'YYYYMM') THEN L."LineTotal" ELSE 0 END) AS "BuAy-1Toplam",
   
    -- 'BugunIlgiliSiparisNumaralari' alanını çekmek için kullanılacak alt sorgu
    COALESCE(
        (
            SELECT STRING_AGG(TO_VARCHAR(DISTINCT_SUBQ."DocNum"), ', ')
            FROM (
                SELECT DISTINCT O."DocNum"
                FROM "TUNADB24"."ORDR" O
                INNER JOIN "TUNADB24"."RDR1" R ON O."DocEntry" = R."DocEntry"
                INNER JOIN "TUNADB24"."DLN1" DL ON R."DocEntry" = DL."BaseEntry" AND R."LineNum" = DL."BaseLine"
                INNER JOIN "TUNADB24"."ODLN" I2 ON DL."DocEntry" = I2."DocEntry"
                WHERE O."CardCode" = C."CardCode"
                    AND O."TaxDate" >= '2023-01-01'
                    AND O."CANCELED" = 'N'
                    AND DAYS_BETWEEN(CURRENT_DATE, I2."TaxDate") = 0
            ) AS DISTINCT_SUBQ
        ), '0'
    ) AS "BugunIlgiliSiparisNumaralari",
  
    -- 'Bugun-1IlgiliSiparisNumaralari' alanını çekmek için kullanılacak alt sorgu
    COALESCE(
        (
            SELECT STRING_AGG(TO_VARCHAR(DISTINCT_SUBQ."DocNum"), ', ')
            FROM (
                SELECT DISTINCT O."DocNum"
                FROM "TUNADB24"."ORDR" O
                INNER JOIN "TUNADB24"."RDR1" R ON O."DocEntry" = R."DocEntry"
                INNER JOIN "TUNADB24"."DLN1" DL ON R."DocEntry" = DL."BaseEntry" AND R."LineNum" = DL."BaseLine"
                INNER JOIN "TUNADB24"."ODLN" I2 ON DL."DocEntry" = I2."DocEntry"
                WHERE O."CardCode" = C."CardCode"
                    AND O."TaxDate" >= '2023-01-01'
                    AND O."CANCELED" = 'N'
                    AND DAYS_BETWEEN(CURRENT_DATE, I2."TaxDate") = -1
            ) AS DISTINCT_SUBQ
        ), '0'
    ) AS "Bugun-1IlgiliSiparisNumaralari",
   
    -- 'Bugun-2IlgiliSiparisNumaralari' alanını çekmek için kullanılacak alt sorgu
    COALESCE(
        (
            SELECT STRING_AGG(TO_VARCHAR(DISTINCT_SUBQ."DocNum"), ', ')
            FROM (
                SELECT DISTINCT O."DocNum"
                FROM "TUNADB24"."ORDR" O
                INNER JOIN "TUNADB24"."RDR1" R ON O."DocEntry" = R."DocEntry"
                INNER JOIN "TUNADB24"."DLN1" DL ON R."DocEntry" = DL."BaseEntry" AND R."LineNum" = DL."BaseLine"
                INNER JOIN "TUNADB24"."ODLN" I2 ON DL."DocEntry" = I2."DocEntry"
                WHERE O."CardCode" = C."CardCode"
                    AND O."TaxDate" >= '2023-01-01'
                    AND O."CANCELED" = 'N'
                    AND DAYS_BETWEEN(CURRENT_DATE, I2."TaxDate") = -2
            ) AS DISTINCT_SUBQ
        ), '0'
    ) AS "Bugun-2IlgiliSiparisNumaralari",

    -- 'Bugun-3IlgiliSiparisNumaralari' alanını çekmek için kullanılacak alt sorgu
    COALESCE(
        (
            SELECT STRING_AGG(TO_VARCHAR(DISTINCT_SUBQ."DocNum"), ', ')
            FROM (
                SELECT DISTINCT O."DocNum"
                FROM "TUNADB24"."ORDR" O
                INNER JOIN "TUNADB24"."RDR1" R ON O."DocEntry" = R."DocEntry"
                INNER JOIN "TUNADB24"."DLN1" DL ON R."DocEntry" = DL."BaseEntry" AND R."LineNum" = DL."BaseLine"
                INNER JOIN "TUNADB24"."ODLN" I2 ON DL."DocEntry" = I2."DocEntry"
                WHERE O."CardCode" = C."CardCode"
                    AND O."TaxDate" >= '2023-01-01'
                    AND O."CANCELED" = 'N'
                    AND DAYS_BETWEEN(CURRENT_DATE, I2."TaxDate") = -3
            ) AS DISTINCT_SUBQ
        ), '0'
    ) AS "Bugun-3IlgiliSiparisNumaralari",
        
        -- 'Bugun-4IlgiliSiparisNumaralari' alanını çekmek için kullanılacak alt sorgu
    COALESCE(
        (
            SELECT STRING_AGG(TO_VARCHAR(DISTINCT_SUBQ."DocNum"), ', ')
            FROM (
                SELECT DISTINCT O."DocNum"
                FROM "TUNADB24"."ORDR" O
                INNER JOIN "TUNADB24"."RDR1" R ON O."DocEntry" = R."DocEntry"
                INNER JOIN "TUNADB24"."DLN1" DL ON R."DocEntry" = DL."BaseEntry" AND R."LineNum" = DL."BaseLine"
                INNER JOIN "TUNADB24"."ODLN" I2 ON DL."DocEntry" = I2."DocEntry"
                WHERE O."CardCode" = C."CardCode"
                    AND O."TaxDate" >= '2023-01-01'
                    AND O."CANCELED" = 'N'
                    AND DAYS_BETWEEN(CURRENT_DATE, I2."TaxDate") = -4
            ) AS DISTINCT_SUBQ
        ), '0'
    ) AS "Bugun-4IlgiliSiparisNumaralari",
   
   -- 'BuAyIlgiliSiparisNumaralari' alanını çekmek için kullanılacak alt sorgu
   COALESCE(
    (
        SELECT STRING_AGG(TO_VARCHAR(DISTINCT_SUBQ."DocNum"), ', ')
        FROM (
            SELECT DISTINCT O."DocNum"
            FROM "TUNADB24"."ORDR" O
            INNER JOIN "TUNADB24"."RDR1" R ON O."DocEntry" = R."DocEntry"
            INNER JOIN "TUNADB24"."DLN1" DL ON R."DocEntry" = DL."BaseEntry" AND R."LineNum" = DL."BaseLine"
            INNER JOIN "TUNADB24"."ODLN" I2 ON DL."DocEntry" = I2."DocEntry"
            WHERE O."CardCode" = C."CardCode"
                AND O."TaxDate" >= '2023-01-01'
                AND O."CANCELED" = 'N'
                AND TO_CHAR(I2."TaxDate", 'YYYYMM') = TO_CHAR(CURRENT_DATE, 'YYYYMM')
        ) AS DISTINCT_SUBQ
    ), '0'
) AS "BuAyIlgiliSiparisNumaralari",

-- 'BuAy-1IlgiliSiparisNumaralari' alanını çekmek için kullanılacak alt sorgu
COALESCE(
    (
        SELECT STRING_AGG(TO_VARCHAR(DISTINCT_SUBQ."DocNum"), ', ')
        FROM (
            SELECT DISTINCT O."DocNum"
            FROM "TUNADB24"."ORDR" O
            INNER JOIN "TUNADB24"."RDR1" R ON O."DocEntry" = R."DocEntry"
            INNER JOIN "TUNADB24"."DLN1" DL ON R."DocEntry" = DL."BaseEntry" AND R."LineNum" = DL."BaseLine"
            INNER JOIN "TUNADB24"."ODLN" I2 ON DL."DocEntry" = I2."DocEntry"
            WHERE O."CardCode" = C."CardCode"
                AND O."TaxDate" >= '2023-01-01'
                AND O."CANCELED" = 'N'
                AND TO_CHAR(I2."TaxDate", 'YYYYMM') = TO_CHAR(ADD_MONTHS(CURRENT_DATE, -1), 'YYYYMM')
        ) AS DISTINCT_SUBQ
    ), '0'
) AS "BuAy-1IlgiliSiparisNumaralari",

   -- 'AcikIrsalıyeBelgeNo-Tarih-Tutar' alanını çekmek için kullanılacak alt sorgu
    COALESCE(
    (
        SELECT STRING_AGG(TO_VARCHAR(sub."DocNum") || '-' || TO_CHAR(sub."TaxDate", 'DD.MM.YYY') || '-' || TO_VARCHAR(sub.remaining_amount), '; ')
        FROM (
            SELECT D."DocNum", D."TaxDate", SUM((DL."LineTotal" / DL."Quantity") * (DL."Quantity" - DL."DelivrdQty")) AS remaining_amount
            FROM "TUNADB24"."ODLN" D
            INNER JOIN "TUNADB24"."DLN1" DL ON D."DocEntry" = DL."DocEntry"
            WHERE D."CardCode" = C."CardCode"
              AND D."TaxDate" >= '2024-01-01'
              AND D."CANCELED" = 'N'
              AND DL."LineStatus" = 'O'
            GROUP BY D."DocNum", D."TaxDate"
        ) sub
    ), '0'
) AS "AcikIrsaliyeBelgeNo-Tarih-Tutar",

    
    SUM(CASE WHEN YEARS_BETWEEN(CURRENT_DATE, I."TaxDate") = 0 THEN L."LineTotal" ELSE 0 END) AS "YillikToplam",
    
    COALESCE((SELECT SUM((DL."LineTotal" / DL."Quantity") * (DL."Quantity" - DL."DelivrdQty"))
              FROM "TUNADB24"."DLN1" DL
              WHERE DL."DocEntry" IN (SELECT D."DocEntry"
                                      FROM "TUNADB24"."ODLN" D
                                      WHERE D."CardCode" = C."CardCode"
                                        AND D."TaxDate" >= '2024-01-01'
                                        AND D."CANCELED" = 'N')
                AND DL."LineStatus" = 'O'), 0) AS "AcikSevkiyatToplami",
                
    COALESCE((SELECT SUM((R."LineTotal" / R."Quantity") * R."OpenCreQty")
              FROM "TUNADB24"."ORDR" T
              LEFT JOIN "TUNADB24"."RDR1" R ON T."DocEntry" = R."DocEntry"
              WHERE T."CardCode" = C."CardCode"
                AND T."TaxDate" >= '2023-01-01'
                AND T."CANCELED" = 'N'
                AND T."DocManClsd" = 'N'
                AND R."LineStatus" = 'O'), 0) AS "AcikSiparisToplami",
    COUNT(DISTINCT I."DocEntry") AS "IrsaliyeSayisi"
FROM
    "TUNADB24"."OCRD" C
LEFT JOIN
    "TUNADB24"."ODLN" I ON I."CardCode" = C."CardCode" AND I."TaxDate" >= '2024-01-01' AND I."CANCELED" = 'N'
LEFT JOIN
    "TUNADB24"."DLN1" L ON I."DocEntry" = L."DocEntry"
LEFT JOIN
    "TUNADB24"."OSLP" S ON C."SlpCode" = S."SlpCode"
LEFT JOIN
    "TUNADB24"."OCRG" G ON C."GroupCode" = G."GroupCode"
GROUP BY
    C."CardCode",
    C."CardName",
    S."SlpName",
    G."GroupName"
HAVING
    (SUM(CASE WHEN DAYS_BETWEEN(CURRENT_DATE, I."TaxDate") = 0 THEN L."LineTotal" ELSE 0 END) +
    SUM(CASE WHEN I."TaxDate" BETWEEN ADD_DAYS(CURRENT_DATE, -10) AND CURRENT_DATE THEN L."LineTotal" ELSE 0 END) +
    SUM(CASE WHEN TO_CHAR(I."TaxDate", 'YYYYMM') = TO_CHAR(CURRENT_DATE, 'YYYYMM') THEN L."LineTotal" ELSE 0 END) +
    SUM(CASE WHEN YEARS_BETWEEN(CURRENT_DATE, I."TaxDate") = 0 THEN L."LineTotal" ELSE 0 END) +
    COALESCE((SELECT SUM((DL."LineTotal" / DL."Quantity") * (DL."Quantity" - DL."DelivrdQty"))
              FROM "TUNADB24"."DLN1" DL
              WHERE DL."DocEntry" IN (SELECT D."DocEntry"
                                      FROM "TUNADB24"."ODLN" D
                                      WHERE D."CardCode" = C."CardCode"
                                        AND D."TaxDate" >= '2024-01-01'
                                        AND D."CANCELED" = 'N')
                AND DL."LineStatus" = 'O'), 0) +
    COALESCE((SELECT SUM((R."LineTotal" / R."Quantity") * R."OpenCreQty")
              FROM "TUNADB24"."ORDR" T
              LEFT JOIN "TUNADB24"."RDR1" R ON T."DocEntry" = R."DocEntry"
              WHERE T."CardCode" = C."CardCode"
                AND T."TaxDate" >= '2023-01-01'
                AND T."CANCELED" = 'N'
                AND T."DocManClsd" = 'N'
                AND R."LineStatus" = 'O'), 0)) > 10
ORDER BY
    "YillikToplam" DESC;

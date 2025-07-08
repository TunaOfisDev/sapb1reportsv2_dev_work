deliverydocsum
*****
SELECT
    S."SlpName" AS "Temsilci",
    G."GroupName" AS "CariGrup",
    C."CardCode" AS "CariKod",
    C."CardName" AS "CariAdi",  
   
   
    SUM(CASE WHEN DAYS_BETWEEN(CURRENT_DATE, I."TaxDate") = 0 THEN L."LineTotal" ELSE 0 END) AS "GunlukToplam",
    -- 'IlgiliSiparisNumaralari' alanını çekmek için kullanılacak alt sorgu
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
    ) AS "GunlukIlgiliSiparisNumaralari",
    SUM(CASE WHEN DAYS_BETWEEN(CURRENT_DATE, I."TaxDate") = -1 THEN L."LineTotal" ELSE 0 END) AS "DunToplam",
    -- 'IlgiliSiparisNumaralari' alanını çekmek için kullanılacak alt sorgu
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
    ) AS "DunIlgiliSiparisNumaralari",
    SUM(CASE WHEN DAYS_BETWEEN(CURRENT_DATE, I."TaxDate") = -2 THEN L."LineTotal" ELSE 0 END) AS "OncekiGunToplam",
    -- 'IlgiliSiparisNumaralari' alanını çekmek için kullanılacak alt sorgu
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
    ) AS "OncekiGunIlgiliSiparisNumaralari",

   
    SUM(CASE WHEN TO_CHAR(I."TaxDate", 'YYYYMM') = TO_CHAR(CURRENT_DATE, 'YYYYMM') THEN L."LineTotal" ELSE 0 END) AS "AylikToplam",
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
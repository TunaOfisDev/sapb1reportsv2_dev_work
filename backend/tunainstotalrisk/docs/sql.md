WITH AcikSiparisler AS (
    SELECT
        O."CardCode",
        SUM(R."LineTotal") AS "AcikSiparisTutari"
    FROM
        "TUNADB24"."ORDR" O
    INNER JOIN "TUNADB24"."RDR1" R ON O."DocEntry" = R."DocEntry"
    WHERE
        R."LineStatus" = 'O'
    GROUP BY
        O."CardCode"
)
SELECT
    T1."SlpName" AS "Satici",
    T3."GroupName" AS "Grup",
    T0."CardCode" AS "MuhatapKod",
    T0."ChannlBP" AS "AvansKod",
    T0."CardName" AS "MuhatapAd",
    CASE WHEN COALESCE(T0."Balance", 0) < 0 THEN 0 ELSE COALESCE(T0."Balance", 0) END AS "Bakiye",
    COALESCE(T0."DNotesBal", 0) AS "AcikTeslimat",
    COALESCE(ASi."AcikSiparisTutari", 0) AS "AcikSiparis",
    CASE WHEN COALESCE(T0."Balance", 0) < 0 THEN COALESCE(T0."Balance", 0) ELSE COALESCE(T2."Balance", 0) END AS "AvansBakiye",
    (COALESCE(T0."Balance", 0) + COALESCE(T0."DNotesBal", 0) + COALESCE(T0."OrdersBal", 0) + COALESCE(T2."Balance", 0)) AS "ToplamRisk"
    
FROM
    "TUNADB24".OCRD T0
LEFT JOIN "TUNADB24"."OSLP" T1 ON T0."SlpCode" = T1."SlpCode"
LEFT JOIN "TUNADB24"."OCRD" T2 ON T0."ChannlBP" = T2."CardCode"
LEFT JOIN "TUNADB24"."OCRG" T3 ON T0."GroupCode" = T3."GroupCode"
LEFT JOIN AcikSiparisler ASi ON T0."CardCode" = ASi."CardCode"
WHERE
    T0."CardCode" LIKE '120%' AND
        T0."CardCode" NOT IN ('120.01.0000280',
							'120.01.0001241',
							'120.01.0001276',
							'120.01.0001296',
							'120.02.0000013',
							'120.07.0000054',
							'120.10.0000001',
							'120.12.0000001',
							'120.90.0000075',
							'120.90.0000511',
							'120.99.0000083') AND
    T0."CardName" NOT LIKE '%AVANS%' AND
    (T0."Balance" + T0."DNotesBal" + T0."OrdersBal" - COALESCE(T2."Balance", 0)) != 0
ORDER BY
    "AcikSiparis" DESC;
-- salesbudget

WITH CTE_Sales AS (
    SELECT
        CASE
            WHEN SUBSTRING(T0."U_sales_type", 1, 10) = 'IDC' THEN 'IDC'
            WHEN SUBSTRING(T0."U_sales_type", 1, 10) = 'ASSMANN' THEN 'ASSMANN'
            ELSE T2."SlpName"
        END AS "Satici",
        EXTRACT(YEAR FROM T0."TaxDate") AS "Yil",
        EXTRACT(MONTH FROM T0."TaxDate") AS "Ay",
        SUM(T1."LineTotal") AS "GercekTutar"

    FROM
        "TUNADB24"."ORDR" T0
    LEFT JOIN "TUNADB24"."RDR1" T1 ON T0."DocEntry" = T1."DocEntry"
    LEFT JOIN "TUNADB24"."OSLP" T2 ON T0."SlpCode" = T2."SlpCode"
    WHERE
        EXTRACT(YEAR FROM T0."TaxDate") = 2024 AND
        T0."CANCELED" = 'N' AND
        T2."SlpName" IS NOT NULL AND
        T2."SlpName" NOT IN ('Melike Ergün', 'Esin Öner', 'Kamer Dülgeroğlu')
    GROUP BY
        CASE
            WHEN SUBSTRING(T0."U_sales_type", 1, 10) = 'IDC' THEN 'IDC'
            WHEN SUBSTRING(T0."U_sales_type", 1, 10) = 'ASSMANN' THEN 'ASSMANN'
            ELSE T2."SlpName"
        END,
        EXTRACT(YEAR FROM T0."TaxDate"),
        EXTRACT(MONTH FROM T0."TaxDate")
),
CTE_Targets AS (
    SELECT 
        Z0."U_satici" AS "Satici",
        EXTRACT(YEAR FROM TO_DATE(Z0."U_tarih")) AS "Yil",
        EXTRACT(MONTH FROM TO_DATE(Z0."U_tarih")) AS "Ay",
        SUM(TO_DECIMAL(REPLACE(REPLACE(Z0."U_hedef_eur", '.', ''), ',', '.')) * 
            TO_DECIMAL(REPLACE(REPLACE(Z0."U_kur", '.', ''), ',', '.'))) AS "HedefTutari"
    FROM 
        "TUNADB24"."@Z_SALES_TARGET_24" Z0
    GROUP BY Z0."U_satici", EXTRACT(YEAR FROM TO_DATE(Z0."U_tarih")), EXTRACT(MONTH FROM TO_DATE(Z0."U_tarih"))
),
CTE_Combined AS (
    SELECT 
        COALESCE(S."Satici", T."Satici") AS "Satici",
        COALESCE(S."Yil", T."Yil") AS "Yil",
        COALESCE(S."Ay", T."Ay") AS "Ay",
        COALESCE(S."GercekTutar", 0) AS "GercekTutar",
        COALESCE(T."HedefTutari", 0) AS "HedefTutari"
    FROM 
        CTE_Sales S
    FULL OUTER JOIN 
        CTE_Targets T ON S."Satici" = T."Satici" AND S."Yil" = T."Yil" AND S."Ay" = T."Ay"
)
SELECT
    "Satici",
    SUM("GercekTutar") AS "Toplam_Gercek",
    SUM("HedefTutari") AS "Toplam_Hedef",
    
    MAX(COALESCE(CASE WHEN "Ay" = 1 THEN "GercekTutar" END, 0)) AS "Oca_Gercek",
    MAX(COALESCE(CASE WHEN "Ay" = 1 THEN "HedefTutari" END, 0)) AS "Oca_Hedef",
    
    MAX(COALESCE(CASE WHEN "Ay" = 2 THEN "GercekTutar" END, 0)) AS "Şub_Gercek",
    MAX(COALESCE(CASE WHEN "Ay" = 2 THEN "HedefTutari" END, 0)) AS "Şub_Hedef",
    
    MAX(COALESCE(CASE WHEN "Ay" = 3 THEN "GercekTutar" END, 0)) AS "Mar_Gercek",
    MAX(COALESCE(CASE WHEN "Ay" = 3 THEN "HedefTutari" END, 0)) AS "Mar_Hedef",
    
    MAX(COALESCE(CASE WHEN "Ay" = 4 THEN "GercekTutar" END, 0)) AS "Nis_Gercek",
    MAX(COALESCE(CASE WHEN "Ay" = 4 THEN "HedefTutari" END, 0)) AS "Nis_Hedef",
    
    MAX(COALESCE(CASE WHEN "Ay" = 5 THEN "GercekTutar" END, 0)) AS "May_Gercek",
    MAX(COALESCE(CASE WHEN "Ay" = 5 THEN "HedefTutari" END, 0)) AS "May_Hedef",
    
    MAX(COALESCE(CASE WHEN "Ay" = 6 THEN "GercekTutar" END, 0)) AS "Haz_Gercek",
    MAX(COALESCE(CASE WHEN "Ay" = 6 THEN "HedefTutari" END, 0)) AS "Haz_Hedef",
    
    MAX(COALESCE(CASE WHEN "Ay" = 7 THEN "GercekTutar" END, 0)) AS "Tem_Gercek",
    MAX(COALESCE(CASE WHEN "Ay" = 7 THEN "HedefTutari" END, 0)) AS "Tem_Hedef",
    
    MAX(COALESCE(CASE WHEN "Ay" = 8 THEN "GercekTutar" END, 0)) AS "Ağu_Gercek",
    MAX(COALESCE(CASE WHEN "Ay" = 8 THEN "HedefTutari" END, 0)) AS "Ağu_Hedef",
    
    MAX(COALESCE(CASE WHEN "Ay" = 9 THEN "GercekTutar" END, 0)) AS "Eyl_Gercek",
    MAX(COALESCE(CASE WHEN "Ay" = 9 THEN "HedefTutari" END, 0)) AS "Eyl_Hedef",
    
    MAX(COALESCE(CASE WHEN "Ay" = 10 THEN "GercekTutar" END, 0)) AS "Eki_Gercek",
    MAX(COALESCE(CASE WHEN "Ay" = 10 THEN "HedefTutari" END, 0)) AS "Eki_Hedef",
    
    MAX(COALESCE(CASE WHEN "Ay" = 11 THEN "GercekTutar" END, 0)) AS "Kas_Gercek",
    MAX(COALESCE(CASE WHEN "Ay" = 11 THEN "HedefTutari" END, 0)) AS "Kas_Hedef",
    
    MAX(COALESCE(CASE WHEN "Ay" = 12 THEN "GercekTutar" END, 0)) AS "Ara_Gercek",
    MAX(COALESCE(CASE WHEN "Ay" = 12 THEN "HedefTutari" END, 0)) AS "Ara_Hedef"
FROM 
    CTE_Combined
GROUP BY
    "Satici"
ORDER BY 
    "Toplam_Gercek" DESC, "Satici";

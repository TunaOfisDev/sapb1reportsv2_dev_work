---bomcomponent sql
WITH ValidProducts AS (
    SELECT DISTINCT
        T0."ItemCode",
        T0."ItemName"
    FROM "TUNADB24"."OITM" T0
    JOIN "TUNADB24"."OITT" T1
       ON T0."ItemCode" = T1."Code"
    WHERE T0."ItmsGrpCod" = 105
      AND T0."ItemCode" = '82393910015'
),

Level0 AS (
    SELECT
        T0."Code" AS "ParentItem",
        T1."Code" AS "ComponentItem",
        T1."Quantity",
        T1."Type",
        0 AS "Level",
        T0."Code" AS "MainItem",
        COALESCE(NULLIF(T0."Code", '?'), NULL) AS "SubItem"
    FROM "TUNADB24"."OITT" T0
    JOIN "TUNADB24"."ITT1" T1
      ON T0."Code" = T1."Father"
    WHERE T0."Code" IN (SELECT "ItemCode" FROM ValidProducts)
),
Level1 AS (
    SELECT
        L0."ComponentItem" AS "ParentItem",
        T1."Code" AS "ComponentItem",
        L0."Quantity" * T1."Quantity" AS "Quantity",
        T1."Type",
        1 AS "Level",
        L0."MainItem",
        COALESCE(NULLIF(L0."ComponentItem", '?'), L0."MainItem") AS "SubItem"
    FROM Level0 L0
    JOIN "TUNADB24"."ITT1" T1
      ON L0."ComponentItem" = T1."Father"
),
Level2 AS (
    SELECT
        L1."ComponentItem" AS "ParentItem",
        T1."Code" AS "ComponentItem",
        L1."Quantity" * T1."Quantity" AS "Quantity",
        T1."Type",
        2 AS "Level",
        L1."MainItem",
        COALESCE(NULLIF(L1."ComponentItem", '?'), L1."MainItem") AS "SubItem"
    FROM Level1 L1
    JOIN "TUNADB24"."ITT1" T1
      ON L1."ComponentItem" = T1."Father"
),
Level3 AS (
    SELECT
        L2."ComponentItem" AS "ParentItem",
        T1."Code" AS "ComponentItem",
        L2."Quantity" * T1."Quantity" AS "Quantity",
        T1."Type",
        3 AS "Level",
        L2."MainItem",
        COALESCE(NULLIF(L2."ComponentItem", '?'), L2."MainItem") AS "SubItem"
    FROM Level2 L2
    JOIN "TUNADB24"."ITT1" T1
      ON L2."ComponentItem" = T1."Father"
),
Level4 AS (
    SELECT
        L3."ComponentItem" AS "ParentItem",
        T1."Code" AS "ComponentItem",
        L3."Quantity" * T1."Quantity" AS "Quantity",
        T1."Type",
        4 AS "Level",
        L3."MainItem",
        COALESCE(NULLIF(L3."ComponentItem", '?'), L3."MainItem") AS "SubItem"
    FROM Level3 L3
    JOIN "TUNADB24"."ITT1" T1
      ON L3."ComponentItem" = T1."Father"
),

AllLevels AS (
    SELECT * FROM Level0
    UNION ALL
    SELECT * FROM Level1
    UNION ALL
    SELECT * FROM Level2
    UNION ALL
    SELECT * FROM Level3
    UNION ALL
    SELECT * FROM Level4
),

/* Burada OSPP tablosunu da join ediyoruz.
   OSPP tablosunda "ItemCode", "Price", "Currency" olduğunu varsayıyoruz. */
SalesPrices AS (
    SELECT
        T0."ItemCode",

        /* 1) Önce ITM1 (PriceList=1) Price'ı al
           2) eğer 0 veya NULL ise OSPP."Price"
           3) aksi halde 0
        */
        CASE
            WHEN (T1."Price" IS NOT NULL AND T1."Price" <> 0)
                 THEN T1."Price"
            WHEN OSPP."Price" IS NOT NULL AND OSPP."Price" <> 0
                 THEN OSPP."Price"
            ELSE 0
        END AS "SalesPrice",

        /* Döviz cinsi de aynı mantıkla: önce ITM1, yoksa OSPP, yoksa TRY */
        CASE
            WHEN (T1."Currency" IS NOT NULL
                  AND T1."Currency" <> ''
                  AND T1."Currency" <> '?')
                 THEN T1."Currency"
            WHEN (OSPP."Currency" IS NOT NULL
                  AND OSPP."Currency" <> ''
                  AND OSPP."Currency" <> '?')
                 THEN OSPP."Currency"
            ELSE 'TRY'
        END AS "SalesCurrency",

        /* PriceListName:
           1) eğer ITM1 Price devredeyse OPLN."ListName"
           2) yoksa OSPP devredeyse 'OSPP Price'
           3) aksi 'YOK'
        */
        CASE
            WHEN (T1."Price" IS NOT NULL AND T1."Price" <> 0)
                 THEN COALESCE(T2."ListName", 'YOK')
            WHEN (OSPP."Price" IS NOT NULL AND OSPP."Price" <> 0)
                 THEN 'OSPP Price'
            ELSE 'YOK'
        END AS "PriceListName"

    FROM "TUNADB24"."OITM" T0

    /* Taban Fiyat Listesi=1 */
    LEFT JOIN "TUNADB24"."ITM1" T1
           ON T0."ItemCode" = T1."ItemCode"
          AND T1."PriceList" = 1

    /* PriceListName from OPLN */
    LEFT JOIN "TUNADB24"."OPLN" T2
           ON T1."PriceList" = T2."ListNum"

    /* OSPP tablosu: eğer T1."Price"=0 ise fallback => OSPP."Price" */
    LEFT JOIN "TUNADB24"."OSPP" OSPP
           ON T0."ItemCode" = OSPP."ItemCode"

    WHERE T0."ItmsGrpCod" = 105
),

CurrentRates AS (
    SELECT
        R."Currency",
        R."Rate" AS "CurrentRate"
    FROM "TUNADB24"."ORTT" R
    WHERE R."RateDate" = CURRENT_DATE
),

/* Burada OPDN."DocCur" yerine PDN1."Currency" kullanılıyor. */
LatestDeliveryPrices AS (
    SELECT
        PDN1."ItemCode",
        FIRST_VALUE(PDN1."Price") OVER (
            PARTITION BY PDN1."ItemCode"
            ORDER BY OPDN."DocDate" DESC, OPDN."DocTime" DESC
        ) AS "GRPrice",

        /* Burada PDN1."Currency" null veya boş ise TRY'ye fallback yapıyoruz */
        FIRST_VALUE(
            CASE
                WHEN PDN1."Currency" IS NOT NULL 
                     AND PDN1."Currency" <> '' 
                     AND PDN1."Currency" <> '?' 
                THEN PDN1."Currency"
                ELSE 'TRY'
            END
        ) OVER (
            PARTITION BY PDN1."ItemCode"
            ORDER BY OPDN."DocDate" DESC, OPDN."DocTime" DESC
        ) AS "GRCurrency",

        FIRST_VALUE(OPDN."DocDate") OVER (
            PARTITION BY PDN1."ItemCode"
            ORDER BY OPDN."DocDate" DESC, OPDN."DocTime" DESC
        ) AS "GRDocDate"
    FROM "TUNADB24"."PDN1" PDN1
    JOIN "TUNADB24"."OPDN" OPDN
      ON PDN1."DocEntry" = OPDN."DocEntry"
    WHERE PDN1."Price" > 0
),

PurchaseList2 AS (
    SELECT
        ITM2."ItemCode",
        ITM2."Price" AS "List2Price",
        CASE
            WHEN ITM2."Currency" IS NULL
                 OR ITM2."Currency" = ''
                 OR ITM2."Currency" = '?' THEN 'TRY'
            ELSE ITM2."Currency"
        END AS "List2Currency"
    FROM "TUNADB24"."ITM1" ITM2
    WHERE ITM2."PriceList" = 2
),

NewLastPurchasePrices AS (
    SELECT
        T0."ItemCode",
        CASE
            WHEN LDP."GRPrice" IS NOT NULL THEN LDP."GRPrice"
            WHEN PL2."List2Price" IS NOT NULL THEN PL2."List2Price"
            ELSE 0
        END AS "LastPurchasePrice",
        CASE
            WHEN LDP."GRCurrency" IS NOT NULL AND LDP."GRCurrency" <> ''
                 THEN LDP."GRCurrency"
            WHEN PL2."List2Currency" IS NOT NULL AND PL2."List2Currency" <> ''
                 THEN PL2."List2Currency"
            ELSE 'TRY'
        END AS "Currency",
        CASE
            WHEN LDP."GRPrice" IS NOT NULL THEN LDP."GRDocDate"
            ELSE NULL
        END AS "DocDate",
        CASE
            WHEN LDP."GRPrice" IS NOT NULL THEN 'İrsaliye'
            WHEN PL2."List2Price" IS NOT NULL AND PL2."List2Price" <> 0 THEN 'Fiyat Listesi'
            ELSE 'Fiyat Yok'
        END AS "PriceSource"
    FROM "TUNADB24"."OITM" T0
    LEFT JOIN LatestDeliveryPrices LDP
           ON T0."ItemCode" = LDP."ItemCode"
    LEFT JOIN PurchaseList2 PL2
           ON T0."ItemCode" = PL2."ItemCode"
),

NewLastPurchasePricesWithRate AS (
    SELECT
        NLP."ItemCode",
        NLP."LastPurchasePrice",
        NLP."Currency",
        NLP."DocDate",
        NLP."PriceSource",
        CASE
            WHEN NLP."Currency" = 'USD' THEN COALESCE(CR_USD."CurrentRate", 1)
            WHEN NLP."Currency" = 'EUR' THEN COALESCE(CR_EUR."CurrentRate", 1)
            ELSE 1
        END AS "Rate",
        CASE
            WHEN NLP."Currency" = 'USD' THEN NLP."LastPurchasePrice" * COALESCE(CR_USD."CurrentRate", 1)
            WHEN NLP."Currency" = 'EUR' THEN NLP."LastPurchasePrice" * COALESCE(CR_EUR."CurrentRate", 1)
            ELSE NLP."LastPurchasePrice"
        END AS "LastPurchasePriceUPB"
    FROM NewLastPurchasePrices NLP
    LEFT JOIN CurrentRates CR_USD 
           ON CR_USD."Currency" = 'USD'
    LEFT JOIN CurrentRates CR_EUR 
           ON CR_EUR."Currency" = 'EUR'
),

ComponentData AS (
    SELECT DISTINCT
        AL."MainItem",
        COALESCE(NULLIF(AL."SubItem", '?'), AL."MainItem") AS "SubItem",
        AL."ComponentItem" AS "ComponentItemCode",
        OITM2."ItemName" AS "ComponentItemName",
        TO_DECIMAL(COALESCE(AL."Quantity", 0), 10, 2) AS "Quantity",
        AL."Level",
        CASE
            WHEN AL."Type" = '4' THEN 'Kalem'
            WHEN AL."Type" = '290' THEN 'Kaynak'
            WHEN AL."Type" = '-18' THEN 'Metin'
            WHEN AL."Type" = '296' THEN 'Rota aşaması'
            ELSE 'Diğer'
        END AS "TypeDescription",
        NLPWR."LastPurchasePrice",
        NLPWR."Currency",
        NLPWR."Rate",
        NLPWR."LastPurchasePriceUPB",
        NLPWR."PriceSource",
        NLPWR."DocDate",
        (TO_DECIMAL(COALESCE(AL."Quantity", 0), 10, 2)
         * TO_DECIMAL(COALESCE(NLPWR."LastPurchasePriceUPB", 0), 10, 2)) AS "ComponentCostUPB",
        OITB."ItmsGrpNam" AS "ItemGroupName"
    FROM AllLevels AL
    LEFT JOIN NewLastPurchasePricesWithRate NLPWR
           ON AL."ComponentItem" = NLPWR."ItemCode"
    LEFT JOIN "TUNADB24"."OITM" OITM2
           ON AL."ComponentItem" = OITM2."ItemCode"
    LEFT JOIN "TUNADB24"."OITB" OITB
           ON OITM2."ItmsGrpCod" = OITB."ItmsGrpCod"
    WHERE AL."Type" != '290'
),

HalfProductCosts("HalfProductCode", "TotalHalfCost") AS (
    SELECT
         P."ComponentItemCode" AS "HalfProductCode",
         SUM(C."ComponentCostUPB") AS "TotalHalfCost"
    FROM ComponentData C
    JOIN ComponentData P
      ON C."SubItem" = P."ComponentItemCode"
    WHERE P."ComponentItemCode" LIKE '151%'
    GROUP BY P."ComponentItemCode"
),

AnaMamul AS (
    SELECT
        CD."MainItem",
        CD."MainItem" AS "SubItem",
        CD."MainItem" AS "ComponentItemCode",
        OITM_MAIN."ItemName" AS "ComponentItemName",
        (
            SELECT COALESCE(T0."Qauntity", 0)
            FROM "TUNADB24"."OITT" T0
            WHERE T0."Code" = CD."MainItem"
        ) AS "Quantity",
        -1 AS "Level",
        'Ana Mamül' AS "TypeDescription",
        0 AS "LastPurchasePrice",
        'TRY' AS "Currency",
        1 AS "Rate",
        0 AS "LastPurchasePriceUPB",
        'Taban Fiyat' AS "PriceSource",
        NULL AS "DocDate",
        SUM(CD."ComponentCostUPB") AS "ComponentCostUPB",
        SP."SalesPrice",
        SP."SalesCurrency",
        SP."PriceListName",
        OITB_MAIN."ItmsGrpNam" AS "ItemGroupName"
    FROM ComponentData CD
    LEFT JOIN SalesPrices SP
      ON CD."MainItem" = SP."ItemCode"
    LEFT JOIN "TUNADB24"."OITM" OITM_MAIN
      ON CD."MainItem" = OITM_MAIN."ItemCode"
    LEFT JOIN "TUNADB24"."OITB" OITB_MAIN
      ON OITM_MAIN."ItmsGrpCod" = OITB_MAIN."ItmsGrpCod"
    GROUP BY
        CD."MainItem",
        SP."SalesPrice",
        SP."SalesCurrency",
        SP."PriceListName",
        OITM_MAIN."ItemName",
        OITB_MAIN."ItmsGrpNam"
)

SELECT
    AM."MainItem",
    AM."SubItem",
    AM."ComponentItemCode",
    AM."ComponentItemName",
    AM."Quantity",
    AM."Level",
    AM."TypeDescription",
    AM."LastPurchasePrice",
    AM."Currency",
    AM."Rate",
    AM."LastPurchasePriceUPB",
    AM."PriceSource",
    COALESCE(
       CASE 
           WHEN AM."DocDate" IS NOT NULL 
           THEN TO_VARCHAR(AM."DocDate", 'DD.MM.YYYY') 
       END, 
       TO_VARCHAR(CURRENT_DATE, 'DD.MM.YYYY')
    ) AS "DocDate",
    AM."ComponentCostUPB",
    AM."SalesPrice",
    AM."SalesCurrency",
    AM."PriceListName",
    AM."ItemGroupName"
FROM AnaMamul AM

UNION ALL

SELECT
    CD."MainItem",
    CD."SubItem",
    CD."ComponentItemCode",
    CD."ComponentItemName",
    CD."Quantity",
    CD."Level",
    CD."TypeDescription",
    CASE
        WHEN CD."ComponentItemCode" LIKE '151%'
             THEN COALESCE(HPC."TotalHalfCost", CD."ComponentCostUPB")
        ELSE CD."LastPurchasePrice"
    END AS "LastPurchasePrice",
    CD."Currency",
    CD."Rate",
    CASE
        WHEN CD."ComponentItemCode" LIKE '151%'
             THEN COALESCE(HPC."TotalHalfCost", CD."ComponentCostUPB") / NULLIF(CD."Quantity", 0)
        ELSE CD."LastPurchasePriceUPB"
    END AS "LastPurchasePriceUPB",
    CD."PriceSource",
    COALESCE(
       CASE 
           WHEN CD."DocDate" IS NOT NULL 
           THEN TO_VARCHAR(CD."DocDate", 'DD.MM.YYYY') 
       END, 
       TO_VARCHAR(CURRENT_DATE, 'DD.MM.YYYY')
    ) AS "DocDate",
    CASE
        WHEN CD."ComponentItemCode" LIKE '151%'
             THEN COALESCE(HPC."TotalHalfCost", CD."ComponentCostUPB")
        ELSE CD."ComponentCostUPB"
    END AS "ComponentCostUPB",
    0 AS "SalesPrice",
    'TRY' AS "SalesCurrency",
    'YOK' AS "PriceListName",
    CD."ItemGroupName"
FROM ComponentData CD
LEFT JOIN HalfProductCosts HPC
      ON CD."ComponentItemCode" = HPC."HalfProductCode"
ORDER BY "MainItem", "Level", "ComponentItemCode";



**************************************************
*********bomproduct sq*******************
-- /SQLQueries/MamulListe_BOMCreationUpdateUsers_FormattedDate.sql

SELECT DISTINCT
    /* Temel Stok Bilgileri */
    T0."ItemCode"                      AS "Ürün Kodu",
    T0."ItemName"                      AS "Ürün Adı",
    T0."DfltWH"                        AS "Varsayılan Depo",

    CASE 
        WHEN T0."InvntItem" = 'Y' THEN 'Evet'
        ELSE 'Hayır'
    END AS "Stok Kalemi",

    CASE 
        WHEN T0."SellItem" = 'Y' THEN 'Evet'
        ELSE 'Hayır'
    END AS "Satılabilir",

    CASE 
        WHEN T0."PrchseItem" = 'Y' THEN 'Evet'
        ELSE 'Hayır'
    END AS "Satın Alınabilir",

    /* Satış Fiyat Listesi: (ITM1 > 0 => OPLN.ListName, aksi => 'Müşteri Özel Fiyat' / 'YOK') */
    CASE 
        WHEN (T1."Price" IS NOT NULL AND T1."Price" <> 0)
             THEN COALESCE(T2."ListName", 'YOK')
        WHEN (OSPP."Price" IS NOT NULL AND OSPP."Price" <> 0)
             THEN 'Müşteri Özel Fiyat'
        ELSE 'YOK'
    END AS "Satış Fiyat Listesi",

    /* Satış Fiyatı: ITM1 > 0, aksi OSPP, aksi 0 */
    CASE 
        WHEN (T1."Price" IS NOT NULL AND T1."Price" <> 0)
             THEN T1."Price"
        WHEN (OSPP."Price" IS NOT NULL AND OSPP."Price" <> 0)
             THEN OSPP."Price"
        ELSE 0
    END AS "Satış Fiyatı",

    /* Para Birimi: ITM1 döviz yoksa OSPP döviz, yoksa TRY */
    CASE 
        WHEN (T1."Price" IS NOT NULL AND T1."Price" <> 0) 
             THEN COALESCE(T1."Currency", 'TRY')
        WHEN (OSPP."Price" IS NOT NULL AND OSPP."Price" <> 0)
             THEN COALESCE(OSPP."Currency", 'TRY')
        ELSE 'TRY'
    END AS "Para Birimi",

    /* BOM Oluşturma/Güncelleme Tarihleri formatlı */
    TO_VARCHAR(T3."CreateDate", 'DD.MM.YYYY') AS "BOM Oluşturma Tarihi",
    TO_VARCHAR(T3."UpdateDate", 'DD.MM.YYYY') AS "BOM Güncelleme Tarihi",

    /* Kullanıcı Kodları (OITT.UserSign / .UserSign2 => OUSR.USERID => USER_CODE) */
    U1."USER_CODE"                     AS "Oluşturan Kullanıcı Kodu",
    U2."USER_CODE"                     AS "Güncelleyen Kullanıcı Kodu"

FROM 
    "TUNADB24"."OITM" T0

/* Ürün ağacı kontrolü => mamul ise OITT tablosunda kaydı olmalı */
INNER JOIN 
    "TUNADB24"."OITT" T3 
    ON T0."ItemCode" = T3."Code"

/* Taban fiyat => PriceList=1 */
LEFT JOIN 
    "TUNADB24"."ITM1" T1 
    ON T0."ItemCode" = T1."ItemCode" 
   AND T1."PriceList" = 1

/* Fiyat Listesi adı */
LEFT JOIN 
    "TUNADB24"."OPLN" T2 
    ON T1."PriceList" = T2."ListNum"

/* Müşteri özel fiyat => OSPP */
LEFT JOIN 
    "TUNADB24"."OSPP" OSPP
    ON T0."ItemCode" = OSPP."ItemCode"

/* Kullanıcılar => OITT.UserSign => OUSR.USERID, OITT.UserSign2 => OUSR.USERID */
LEFT JOIN "TUNADB24"."OUSR" U1 
       ON T3."UserSign"  = U1."USERID"
LEFT JOIN "TUNADB24"."OUSR" U2 
       ON T3."UserSign2" = U2."USERID"

WHERE 
    T0."ItmsGrpCod" = 105  -- Mamül grubu

ORDER BY 
    T0."ItemCode";

crmactivities
****
SELECT
    OCLG."ClgCode"  AS "Numara",
    OCLG."Recontact" AS "BaslangicTarihi",
    AU."U_NAME" AS "Isleyen",
    AB."U_NAME" AS "TayinEden",
   
    CASE 
        WHEN OCLG."Action" = 'C' THEN 'Telefon çağrısı'
        WHEN OCLG."Action" = 'M' THEN 'Toplantı'
        WHEN OCLG."Action" = 'T' THEN 'Görev'
        WHEN OCLG."Action" = 'E' THEN 'Not'
        WHEN OCLG."Action" = 'P' THEN 'Kampanya'
        WHEN OCLG."Action" = 'N' THEN 'Diğer'
    END AS "Aktivite",
  
    
    CASE 
        WHEN OCLG."CntctType" = '-1' THEN 'Genel'
        WHEN OCLG."CntctType" = '1' THEN 'Müşteri Ziyareti'
        else 'Diğer' 
    END AS "Tur",
    
      
    CASE 
      	WHEN OCLG."CntctSbjct" = '3' THEN 'Günlük İşler'
        WHEN OCLG."CntctSbjct" = '12' THEN 'Proje Çalışması'
        WHEN OCLG."CntctSbjct" = '2' THEN 'Randevu Talebi'
        WHEN OCLG."CntctSbjct" = '1' THEN 'Zoom Toplantısı'       
        
        else 'Diğer' 
    END AS "Konu",
    
    
    OCLG."CardCode" AS "MuhatapKod",
    OCRD."CardName" AS "MuhatapAd",

        CASE
    WHEN OCLG."status" = '-2' THEN 'Başlatılmadı'
	WHEN OCLG."status" = '-3' THEN 'Tamamlandı'    
    ELSE 'Tamamlandı'
    END AS "Durum",
    
    
    
    OCLG."Details"  AS "Aciklama",
    OCLG."Notes"    AS "Icerik" 
FROM
    "TUNADB24"."OCLG" OCLG

LEFT JOIN "TUNADB24"."OCRD" OCRD ON OCLG."CardCode" = OCRD."CardCode"
LEFT JOIN "TUNADB24"."OUSR" AU ON OCLG."AttendUser" = AU."USERID"
LEFT JOIN "TUNADB24"."OUSR" AB ON OCLG."AssignedBy" = AB."USERID"
ORDER BY OCLG."ClgCode" ASC
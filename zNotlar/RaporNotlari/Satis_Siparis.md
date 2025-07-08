
https://biuan.com/RDR1


dört önemli noktaya dikkat ederek raporlar oluşturman gerekecek:

"ORDRRD1SQL-4RULES" 

1. İptal edilen satış siparişlerini rapora dahil etmemek için:
   ```sql
   T."CANCELED" = 'N'
   ```

2. Elle kapatılan satış siparişlerini rapora dahil etmemek için:
   ```sql
   T."DocManClsd" = 'N'
   ```

3. RDR1 tablosunda satırların `DocEntry` ve `LineNum` alanlarının birleşiminin unique olmasını sağlamak için:
   ```sql
   WITH DetailData AS (
       SELECT
           T."DocEntry" || '-' || R."LineNum" || '-' || ROW_NUMBER() OVER (PARTITION BY T."DocEntry", R."LineNum" ORDER BY T."DocNum" DESC) AS "UniqDetailNo",
   ) 
   WHERE "rn" = 1
   ```

4. ORDR tablosunda "BelgeOnay" durumu için:
   ```sql
   T."WddStatus" != 'N'
   ```

Bu kuralları uygulayarak daha doğru ve güvenilir raporlar oluşturabilirsin. 
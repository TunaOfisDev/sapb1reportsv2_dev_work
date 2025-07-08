# backend/scripts/posgresqldbsize.sh
#!/bin/bash

# Veritabanı adı
DB_NAME="sapb1reports_v2"

# Sorguyu çalıştır
sudo -u postgres psql -d $DB_NAME -c "
SELECT 
    c.relname AS table_name,
    pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size,
    pg_total_relation_size(c.oid) AS size_in_bytes
FROM 
    pg_class c
LEFT JOIN 
    pg_namespace n ON n.oid = c.relnamespace
WHERE 
    n.nspname = 'public'
ORDER BY 
    size_in_bytes DESC;"

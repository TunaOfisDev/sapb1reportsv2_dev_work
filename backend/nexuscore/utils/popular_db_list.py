# path: backend/nexuscore/utils/popular_db_list.py

"""
Veritabanları ile ilgili tüm bilgilerin (değer, etiket, ikon)
tek ve merkezi Python kaynağı.
Bu dosya, frontend/src/components/NexusCore/utils/populardblist.js
ile senkronize olmalıdır.
"""

# Önce ham veriyi tanımlayalım
_raw_db_list = [
    # Her sözlüğe JS karşılığı gibi 'icon' anahtarı eklendi.
    {'value': 'postgresql', 'label': 'PostgreSQL', 'icon': 'postgresql'},
    {'value': 'mysql', 'label': 'MySQL', 'icon': 'mysql'},
    {'value': 'mariadb', 'label': 'MariaDB', 'icon': 'mysql'}, # MySQL ikonu kullanılabilir
    {'value': 'sql_server', 'label': 'Microsoft SQL Server', 'icon': 'sql-server'},
    {'value': 'sap_hana', 'label': 'SAP HANA', 'icon': 'database'}, # Özel ikonu yoksa genel ikon
    {'value': 'oracle', 'label': 'Oracle Database', 'icon': 'database'},
    {'value': 'sqlite', 'label': 'SQLite', 'icon': 'database'},
    {'value': 'cockroachdb', 'label': 'CockroachDB', 'icon': 'database'},
    {'value': 'tidb', 'label': 'TiDB', 'icon': 'database'},
    {'value': 'amazon_aurora', 'label': 'Amazon Aurora', 'icon': 'database'},
    {'value': 'google_cloud_sql', 'label': 'Google Cloud SQL', 'icon': 'database'},
    {'value': 'azure_sql', 'label': 'Azure SQL Database', 'icon': 'database'},
    {'value': 'mongodb', 'label': 'MongoDB', 'icon': 'database'},
    {'value': 'couchbase', 'label': 'Couchbase', 'icon': 'database'},
    {'value': 'dynamodb', 'label': 'Amazon DynamoDB', 'icon': 'database'},
    {'value': 'firestore', 'label': 'Google Firestore', 'icon': 'database'},
    {'value': 'cosmosdb', 'label': 'Azure Cosmos DB', 'icon': 'database'},
    {'value': 'redis', 'label': 'Redis', 'icon': 'database'},
    {'value': 'cassandra', 'label': 'Apache Cassandra', 'icon': 'database'},
    {'value': 'scylladb', 'label': 'ScyllaDB', 'icon': 'database'},
    {'value': 'neo4j', 'label': 'Neo4j', 'icon': 'database'},
    {'value': 'influxdb', 'label': 'InfluxDB', 'icon': 'database'},
    {'value': 'timescaledb', 'label': 'TimescaleDB', 'icon': 'database'},
    {'value': 'clickhouse', 'label': 'ClickHouse', 'icon': 'database'},
    {'value': 'elasticsearch', 'label': 'Elasticsearch', 'icon': 'search'},
    {'value': 'opensearch', 'label': 'OpenSearch', 'icon': 'search'},
    {'value': 'druid', 'label': 'Apache Druid', 'icon': 'database'},
    {'value': 'pinecone', 'label': 'Pinecone', 'icon': 'database'},
    {'value': 'milvus', 'label': 'Milvus', 'icon': 'database'},
]

# Frontend ile aynı sıralama mantığını uygula: 'label' alanına göre alfabetik sırala.
# Bu, ana "export" edilecek listemizdir.
POPULAR_DB_LIST = sorted(_raw_db_list, key=lambda item: item['label'])


# --- Doğrulama (Validation) için Yardımcı Araçlar ---

# Sadece geçerli 'value' değerlerini içeren bir set (küme).
# Bir 'set' içinde 'in' kontrolü, bir 'list' içindekinden çok daha hızlıdır.
# Serializer'da 'db_type' doğrulaması için bunu kullanacağız.
SUPPORTED_DB_VALUES = {item['value'] for item in POPULAR_DB_LIST}

# Değeri (örn: 'postgresql') Etikete (örn: 'PostgreSQL') çeviren hızlı bir harita (map)
DB_VALUE_TO_LABEL_MAP = {item['value']: item['label'] for item in POPULAR_DB_LIST}
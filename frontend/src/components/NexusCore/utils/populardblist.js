// path: frontend/src/components/NexusCore/utils/populardblist.js

/**
 * Veritabanları ile ilgili tüm bilgilerin (değer, etiket, ikon)
 * tek ve merkezi kaynağı.
 */
const popularDBList = [
  // Her nesneye bir 'icon' anahtarı eklendi.
  { value: 'postgresql', label: 'PostgreSQL', icon: 'postgresql' },
  { value: 'mysql', label: 'MySQL', icon: 'mysql' },
  { value: 'mariadb', label: 'MariaDB', icon: 'mysql' }, // MySQL ikonu kullanılabilir
  { value: 'sql_server', label: 'Microsoft SQL Server', icon: 'sql-server' },
  { value: 'sap_hana', label: 'SAP HANA', icon: 'database' }, // Özel ikonu yoksa genel ikon
  { value: 'oracle', label: 'Oracle Database', icon: 'database' },
  { value: 'sqlite', label: 'SQLite', icon: 'database' },
  { value: 'cockroachdb', label: 'CockroachDB', icon: 'database' },
  { value: 'tidb', label: 'TiDB', icon: 'database' },
  { value: 'amazon_aurora', label: 'Amazon Aurora', icon: 'database' },
  { value: 'google_cloud_sql', label: 'Google Cloud SQL', icon: 'database' },
  { value: 'azure_sql', label: 'Azure SQL Database', icon: 'database' },
  { value: 'mongodb', label: 'MongoDB', icon: 'database' },
  { value: 'couchbase', label: 'Couchbase', icon: 'database' },
  { value: 'dynamodb', label: 'Amazon DynamoDB', icon: 'database' },
  { value: 'firestore', label: 'Google Firestore', icon: 'database' },
  { value: 'cosmosdb', label: 'Azure Cosmos DB', icon: 'database' },
  { value: 'redis', label: 'Redis', icon: 'database' },
  { value: 'cassandra', label: 'Apache Cassandra', icon: 'database' },
  { value: 'scylladb', label: 'ScyllaDB', icon: 'database' },
  { value: 'neo4j', label: 'Neo4j', icon: 'database' },
  { value: 'influxdb', label: 'InfluxDB', icon: 'database' },
  { value: 'timescaledb', label: 'TimescaleDB', icon: 'database' },
  { value: 'clickhouse', label: 'ClickHouse', icon: 'database' },
  { value: 'elasticsearch', label: 'Elasticsearch', icon: 'search' },
  { value: 'opensearch', label: 'OpenSearch', icon: 'search' },
  { value: 'druid', label: 'Apache Druid', icon: 'database' },
  { value: 'pinecone', label: 'Pinecone', icon: 'database' },
  { value: 'milvus', label: 'Milvus', icon: 'database' },
];

popularDBList.sort((a, b) => a.label.localeCompare(b.label));

export default popularDBList;
// path: frontend/src/components/NexusCore/utils/populardblist.js

/**
 * ConnectionForm'daki 'Veritabanı Türü' seçim listesi için
 * popüler veritabanlarının bir listesini içerir.
 * Her öğe, Select bileşenimizle uyumlu { value, label } formatındadır.
 * Liste, kullanıcı deneyimini iyileştirmek için alfabetik olarak sıralanmıştır.
 */
const popularDBList = [
  // Relational (SQL)
  { value: 'postgresql', label: 'PostgreSQL' },
  { value: 'mysql', label: 'MySQL' },
  { value: 'mariadb', label: 'MariaDB' },
  { value: 'sql_server', label: 'Microsoft SQL Server' },
  { value: 'oracle', label: 'Oracle Database' },
  { value: 'sqlite', label: 'SQLite' },
  { value: 'cockroachdb', label: 'CockroachDB (Distributed SQL)' },
  { value: 'sap_hana', label: 'SAP HANA' },
  { value: 'tidb', label: 'TiDB (Distributed SQL)' },
  
  // Cloud Relational
  { value: 'amazon_aurora', label: 'Amazon Aurora' },
  { value: 'google_cloud_sql', label: 'Google Cloud SQL' },
  { value: 'azure_sql', label: 'Azure SQL Database' },

  // NoSQL - Document
  { value: 'mongodb', label: 'MongoDB' },
  { value: 'couchbase', label: 'Couchbase' },
  { value: 'dynamodb', label: 'Amazon DynamoDB' },
  { value: 'firestore', label: 'Google Firestore' },
  { value: 'cosmosdb', label: 'Azure Cosmos DB' },

  // NoSQL - Key-Value
  { value: 'redis', label: 'Redis' },

  // NoSQL - Wide-Column
  { value: 'cassandra', label: 'Apache Cassandra' },
  { value: 'scylladb', label: 'ScyllaDB' },

  // NoSQL - Graph
  { value: 'neo4j', label: 'Neo4j' },

  // Time Series
  { value: 'influxdb', label: 'InfluxDB' },
  { value: 'timescaledb', label: 'TimescaleDB' },

  // Analytics & Search
  { value: 'clickhouse', label: 'ClickHouse' },
  { value: 'elasticsearch', label: 'Elasticsearch' },
  { value: 'opensearch', label: 'OpenSearch' },
  { value: 'druid', label: 'Apache Druid' },
  
  // Vector Databases
  { value: 'pinecone', label: 'Pinecone' },
  { value: 'milvus', label: 'Milvus' },
];

// Listeyi, etiketlere (label) göre alfabetik olarak sırala
popularDBList.sort((a, b) => a.label.localeCompare(b.label));

export default popularDBList;
// frontend/src/api/dynamicreport.js
import axios from './axiosconfig';

// Yeni backend API servisi ile SQL sorgusu listesini al
export const getSqlQueryList = async () => {
  try {
    const response = await axios.get('/dynamicreport/get-sql-query-list/');
    return response.data.map(item => ({
      id: item.id,
      table_name: item.table_name
    }));
  } catch (error) {
    throw error;
  }
};

// Yeni backend API servisi ile SQL tablo listesini al
export const getSqlTableList = async () => {
  try {
    const response = await axios.get('/dynamicreport/sql-table-list/');
    return response.data;
  } catch (error) {
    throw error;
  }
};

// SQL Sorgusu Seçin ve Anlık Veri Al
export const fetchInstantData = async (table_name) => {
  try {
    const response = await axios.get(`/dynamicreport/fetch_instant_data/by_name/${table_name}/`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// SQL Sorgusu Seçin table_name göre
export const getSqlQueryByTableName = async (table_name) => {
  try {
    const response = await axios.get(`/dynamicreport/sql-queries/by_name/${table_name}/`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Manuel başlıkları tablo adına göre al
export const getManualHeadersByTableName = async (table_name) => {
  try {
    const response = await axios.get(`/dynamicreport/manual-headers/by_name/${table_name}/`);
    if (response.data && response.data.length > 0) {
      return response.data.map(item => item.header_name); // Sadece başlık isimlerini al
    } else {
      return []; // Boş bir dizi döndür, başlıklar mevcut değilse
    }
  } catch (error) {
    throw error;
  }
};

// Manuel başlıkları ve tipleri tablo adına göre al
export const getManualHeadersTypesByTableName = async (table_name) => {
  try {
    const response = await axios.get(`/dynamicreport/manual-headers/by_name/${table_name}/`); // Tablo adını kullanarak doğru endpoint'i çağırın
    if (response.data && response.data.length > 0) {
      return response.data.map(item => ({ header_name: item.header_name, type: item.type })); // Başlık adları ve tiplerini al
    } else {
      return []; // Boş bir dizi döndür, başlıklar mevcut değilse
    }
  } catch (error) {
    throw error;
  }
};

// Yeni API servisi ile dinamik tablo oluştur
export const createDynamicTable = async (table_name, data_set) => {
  try {
    const response = await axios.post(`/dynamicreport/create-dynamic-table/${table_name}/`, data_set);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Dinamik Tablo Verilerini Al (Güncellenmiş)
export const getDynamicTableByTableName = async (table_name) => {
  try {
    const response = await axios.get(`/dynamicreport/dynamic-tables/by_name/${table_name}/`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Yeni API servisi ile belirli bir değeri biçimlendirme type format
export const formatValue = async (data_type, value) => {
  try {
    const response = await axios.post('/dynamicreport/format_value/', { data_type, value });
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Alignment bilgilerini al
export const getAlignmentInfoByTableName = async (table_name) => {
  try {
    const response = await axios.get(`/dynamicreport/dynamic-tables/fetch_local_data_with_alignment/${table_name}`);
    return response.data;  // Bu, alignment_indexes ve first_row_example anahtarlarını içerecek.
  } catch (error) {
    throw error;
  }
};

// Yeni API servisi ile test ve rapor oluştur
export const testAndGenerateReport = async (sqlQueryIds) => {
  try {
      const response = await axios.post('/dynamicreport/test-and-generate-report/', { sql_query_ids: sqlQueryIds });
      return response.data;
  } catch (error) {
      throw error;
  }
};




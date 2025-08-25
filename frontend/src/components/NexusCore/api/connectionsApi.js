/* path: frontend/src/components/NexusCore/api/connectionsApi.js */

/* Projenizin ana Axios yapılandırmasını import ediyoruz.
   Bu sayede token yönetimi, baseURL ve hata yakalama gibi tüm merkezi mantığı miras alıyoruz.
   Doğru dosya yolunu projenizin yapısına göre teyit ediniz. */
import axiosInstance from '../../../api/axiosconfig';

const API_ENDPOINT = 'nexuscore/connections/';

/**
 * Tüm veri tabanı bağlantılarını listeler.
 * @returns {Promise<Array>} Bağlantı listesini içeren bir promise döndürür.
 */
export const getConnections = async () => {
  try {
    const response = await axiosInstance.get(API_ENDPOINT);
    return response.data;
  } catch (error) {
    console.error("Veri bağlantıları alınırken hata oluştu:", error);
    /* Hata, merkezi axios interceptor'ı tarafından zaten işleniyor,
       ancak bileşen bazında özel bir işlem yapmak gerekirse burada yakalayabiliriz. */
    throw error;
  }
};

/**
 * Belirli bir ID'ye sahip veri tabanı bağlantısının detaylarını getirir.
 * @param {number} id Bağlantı ID'si.
 * @returns {Promise<Object>} Bağlantı detaylarını içeren bir promise döndürür.
 */
export const getConnectionById = async (id) => {
  try {
    const response = await axiosInstance.get(`${API_ENDPOINT}${id}/`);
    return response.data;
  } catch (error) {
    console.error(`ID'si ${id} olan bağlantı alınırken hata:`, error);
    throw error;
  }
};

/**
 * Yeni bir veri tabanı bağlantısı oluşturur.
 * @param {object} connectionData - { title, db_type, json_config } formatında veri.
 * @returns {Promise<Object>} Oluşturulan yeni bağlantı nesnesini döndürür.
 */
export const createConnection = async (connectionData) => {
  try {
    const response = await axiosInstance.post(API_ENDPOINT, connectionData);
    return response.data;
  } catch (error) {
    console.error("Yeni bağlantı oluşturulurken hata:", error);
    throw error;
  }
};

/**
 * Mevcut bir veri tabanı bağlantısını günceller.
 * @param {number} id Güncellenecek bağlantının ID'si.
 * @param {object} connectionData Güncellenecek alanları içeren nesne.
 * @returns {Promise<Object>} Güncellenmiş bağlantı nesnesini döndürür.
 */
export const updateConnection = async (id, connectionData) => {
  try {
    /* Genellikle sadece değişen alanları göndermek için PATCH kullanmak daha verimlidir. */
    const response = await axiosInstance.patch(`${API_ENDPOINT}${id}/`, connectionData);
    return response.data;
  } catch (error) {
    console.error(`ID'si ${id} olan bağlantı güncellenirken hata:`, error);
    throw error;
  }
};

/**
 * Bir veri tabanı bağlantısını siler.
 * @param {number} id Silinecek bağlantının ID'si.
 * @returns {Promise<void>} İşlem başarılı olduğunda bir promise döndürür.
 */
export const deleteConnection = async (id) => {
  try {
    /* DELETE istekleri genellikle 204 No Content status kodu ile döner ve body'si boştur. */
    await axiosInstance.delete(`${API_ENDPOINT}${id}/`);
  } catch (error) {
    console.error(`ID'si ${id} olan bağlantı silinirken hata:`, error);
    throw error;
  }
};

/**
 * Bir veri tabanı bağlantısını test etmek için backend'deki özel action'ı tetikler.
 * @param {number} id Test edilecek bağlantının ID'si.
 * @returns {Promise<Object>} Test sonucunu içeren nesneyi döndürür.
 */
export const testConnection = async (id) => {
    try {
        const response = await axiosInstance.post(`${API_ENDPOINT}${id}/test/`);
        return response.data;
    } catch (error) {
        console.error(`ID'si ${id} olan bağlantı test edilirken hata:`, error);
        /* Hata durumunda, interceptor genel bir hata mesajı gösterebilir,
           ama biz yine de hatayı bileşene de yollayarak orada özel bir
           aksiyon (örn: butonun kırmızı olması) alabiliriz. */
        throw error;
    }
};
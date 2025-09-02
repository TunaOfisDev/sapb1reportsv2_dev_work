import axiosInstance from '../../../api/axiosconfig';

/**
 * Müşteri Bazlı Satış Özeti (V2) raporu için tüm API isteklerini yönetir.
 * * @module customerSalesApi
 */

/**
 * Filtrelenmiş rapor verilerini, özet toplamları ve filtre seçeneklerini backend'den alır.
 * Bu fonksiyon, rapor sayfasının ihtiyaç duyduğu tüm verileri tek bir istekte getirir.
 * * @async
 * @param {object} filters - Filtreleme için kullanılacak parametreleri içeren nesne.
 * @param {string[]} filters.satici - Seçilen satıcıların listesi.
 * @param {string[]} filters.satis_tipi - Seçilen satış tiplerinin listesi.
 * @param {string[]} filters.cari_grup - Seçilen cari grupların listesi.
 * @returns {Promise<object>} API'den dönen tam veri paketini (data, summary, filterOptions, lastUpdated) döndürür.
 * @throws {Error} API isteği başarısız olursa hata fırlatır.
 */
const getReportData = async (filters) => {
  try {
    // Axios, `params` nesnesindeki dizileri otomatik olarak doğru formatlı
    // query parametrelerine çevirir (örn: ?satici=Caner Atak&satici=Merve Torun)
    const response = await axiosInstance.get('customersales/report/', { params: filters });
    return response.data;
  } catch (error) {
    console.error('Müşteri satış raporu verileri alınırken hata oluştu:', error);
    // Hatanın üst bileşenler tarafından yakalanabilmesi için tekrar fırlatıyoruz.
    throw error;
  }
};

/**
 * HANA'dan veri çekme ve PostgreSQL'e kaydetme işlemini tetikler.
 * Bu fonksiyon, kullanıcının "HANA Veri Çek" butonuna basmasıyla çağrılır.
 * * @async
 * @returns {Promise<object>} Başarılı olduğunda API'den dönen mesaj nesnesini döndürür.
 * @throws {Error} API isteği başarısız olursa hata fırlatır.
 */
const triggerHanaSync = async () => {
  try {
    const response = await axiosInstance.post('customersales/fetch-hana-data/');
    return response.data;
  } catch (error) {
    console.error('HANA veri senkronizasyonu tetiklenirken hata oluştu:', error);
    throw error;
  }
};

// Tüm API fonksiyonlarını tek bir nesne altında toplayıp export ediyoruz.
const customerSalesApi = {
  getReportData,
  triggerHanaSync,
};

export default customerSalesApi;
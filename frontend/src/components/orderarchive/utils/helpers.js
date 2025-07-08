// frontend/src/components/orderarchive/utils/helpers.js

/**
* Tarih formatını düzenler
* @param {string} dateStr - "YYYY-MM-DD" formatında tarih string'i
* @returns {string} "DD.MM.YYYY" formatında tarih string'i
*/
export const formatDate = (dateStr) => {
    if (!dateStr) return '';
    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('tr-TR', {
            day: '2-digit',
            month: '2-digit', 
            year: 'numeric'
        });
    } catch (error) {
        console.error('Tarih formatı hatası:', error);
        return dateStr;
    }
 };
 
 /**
 * Para birimini formatlar
 * @param {number} value - Formatlanacak sayısal değer
 * @param {string} currency - Para birimi (TRY, USD, EUR vb.)
 * @returns {string} Formatlanmış para değeri
 */
 export const formatCurrency = (value, currency = '') => {
    if (!value && value !== 0) return '';
    
    try {
        const formattedValue = new Intl.NumberFormat('tr-TR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
        
        return currency ? `${formattedValue} ${currency}` : formattedValue;
    } catch (error) {
        console.error('Para birimi format hatası:', error);
        return value.toString();
    }
 };
 
 /**
 * Miktarları formatlar
 * @param {number} value - Formatlanacak miktar
 * @returns {string} Formatlanmış miktar
 */
 export const formatQuantity = (value) => {
    if (!value && value !== 0) return '';
    
    try {
        return new Intl.NumberFormat('tr-TR', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 4
        }).format(value);
    } catch (error) {
        console.error('Miktar format hatası:', error);
        return value.toString();
    }
 };
 
 /**
 * Tablodan gelen verileri export formatına dönüştürür
 * @param {Array} data - Tablo verileri
 * @returns {Array} Export için formatlanmış veriler
 */
 export const prepareExportData = (data) => {
    if (!Array.isArray(data)) return [];
    
    return data.map(item => ({
        'Satıcı': item.seller || '',
        'Sipariş No': item.order_number || '',
        'Sipariş Tarihi': formatDate(item.order_date),
        'Teslim Tarihi': formatDate(item.delivery_date),
        'Ülke': item.country || '',
        'Şehir': item.city || '',
        'Müşteri Kodu': item.customer_code || '',
        'Müşteri Adı': item.customer_name || '',
        'Belge Açıklama': item.document_description || '',
        'Ürün Kodu': item.item_code || '',
        'Ürün Açıklama': item.item_description || '',
        'Miktar': formatQuantity(item.quantity),
        'Birim Fiyat': formatCurrency(item.unit_price, item.currency),
        'Para Birimi': item.currency || '',
        'Kur': formatQuantity(item.exchange_rate)
    }));
 };
 
 /**
 * API'den gelen hata mesajlarını formatlar
 * @param {Error} error - Hata objesi
 * @returns {string} Formatlanmış hata mesajı
 */
 export const formatErrorMessage = (error) => {
    if (!error) return 'Bilinmeyen hata';
    
    if (error.response) {
        // API'den dönen hata
        return error.response.data.error || error.response.data.message || 'API hatası';
    } else if (error.request) {
        // İstek yapıldı ama cevap alınamadı
        return 'Sunucuya ulaşılamıyor';
    } else {
        // İstek oluşturulurken hata oluştu
        return error.message || 'Bir hata oluştu';
    }
 };
 
 /**
 * Büyük veri setlerini chunk'lara böler
 * @param {Array} array - Bölünecek array
 * @param {number} size - Chunk boyutu
 * @returns {Array} Chunk'lara bölünmüş array
 */
 export const chunkArray = (array, size = 100) => {
    if (!Array.isArray(array)) return [];
    
    const chunks = [];
    for (let i = 0; i < array.length; i += size) {
        chunks.push(array.slice(i, i + size));
    }
    return chunks;
 };
 
 /**
 * URL için query parametrelerini oluşturur
 * @param {Object} params - Query parametreleri
 * @returns {string} URL query string
 */
 export const buildQueryString = (params) => {
    if (!params || typeof params !== 'object') return '';
    
    const query = Object.entries(params)
        .filter(([_, value]) => value !== null && value !== undefined && value !== '')
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
        .join('&');
        
    return query ? `?${query}` : '';
 };
 
 /**
 * Arama sorgusunu normalize eder
 * @param {string} query - Ham sorgu metni
 * @returns {string} Normalize edilmiş sorgu
 */
 export const normalizeQuery = (query) => {
    if (!query) return '';
    
    return query
        .trim()
        .toLowerCase()
        .replace(/\s+/g, ' '); // Birden fazla boşluğu tek boşluğa indirir
};
 
 /**
 * Döviz değerlerini TL'ye çevirir
 * @param {number} value - Döviz değeri
 * @param {number} exchangeRate - Döviz kuru
 * @returns {number} TL değeri
 */
 export const convertToTRY = (value, exchangeRate) => {
    if (!value || !exchangeRate) return 0;
    return value * exchangeRate;
 };
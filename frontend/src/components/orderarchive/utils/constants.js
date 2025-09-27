// frontend/src/components/orderarchive/utils/constants.js
import { formatDate } from './dateFormat';

/**
 * Sipariş arşivi için yıl listesi (2005-2023)
 */
export const YEARS = Array.from({ length: 19 }, (_, index) => 2005 + index);

/**
 * Sayfa başına kayıt sayısı seçenekleri
 */
export const PAGE_SIZE_OPTIONS = [
    { value: 50, label: '50 Kayıt' },
    { value: 100, label: '100 Kayıt' },
    { value: 250, label: '250 Kayıt' },
    { value: 500, label: '500 Kayıt' }
];

/**
 * Varsayılan sayfalama değerleri
 */
export const PAGINATION_DEFAULTS = {
    PAGE_SIZE: 100,
    CURRENT_PAGE: 1
};

// frontend/src/components/orderarchive/utils/constants.js

/**
 * Tablo kolonları için sabit tanımlamalar
 * accessor: API'den gelen veri anahtarı
 * Header: Görüntülenecek başlık
 * width: Kolonun genişliği
 * sortable: Sıralanabilir mi?
 * filterable: Filtrelenebilir mi?
 * align: Hücre içeriği hizalama ('left', 'right', 'center')
 */
export const TABLE_COLUMNS = [
    { accessor: 'seller', Header: 'Satıcı', width: 120, sortType: 'alphanumeric', sortable: true, filterable: true },
    { accessor: 'order_number', Header: 'Sipariş No', width: 130, sortType: 'numeric', sortable: true, filterable: true },
    {
        accessor: 'order_date',
        Header: 'Sipariş Tarihi',
        width: 120,
        sortType: (rowA, rowB, columnId) => {
            const dateA = new Date(rowA.values[columnId]);
            const dateB = new Date(rowB.values[columnId]);
            return dateA - dateB;
        },
        sortable: true,
        filterable: true,
        Cell: ({ value }) => formatDate(value), // Tarih formatlama
    },
    { accessor: 'year', Header: 'Yıl', width: 100, sortType: 'numeric', sortable: true, filterable: true },
    { accessor: 'month', Header: 'Ay', width: 100, sortType: 'numeric', sortable: true, filterable: true },
    { accessor: 'country', Header: 'Ülke', width: 120, sortType: 'alphanumeric', sortable: true, filterable: true },
    { accessor: 'city', Header: 'Şehir', width: 120, sortType: 'alphanumeric', sortable: true, filterable: true },
    { accessor: 'customer_code', Header: 'Müşteri Kodu', width: 130, sortType: 'alphanumeric', sortable: true, filterable: true },
    { accessor: 'customer_name', Header: 'Müşteri Adı', width: 200, sortType: 'alphanumeric', sortable: true, filterable: true },
    { accessor: 'document_description', Header: 'Belge Açıklama', width: 200, sortType: 'alphanumeric', sortable: true, filterable: true },
    { accessor: 'color_code', Header: 'Renk Kodu', width: 120, sortType: 'alphanumeric', sortable: true, filterable: true },
    { accessor: 'item_code', Header: 'Kalem Kodu', width: 130, sortType: 'alphanumeric', sortable: true, filterable: true },
    { accessor: 'item_description', Header: 'Kalem Tanım', width: 200, sortType: 'alphanumeric', sortable: true, filterable: true },
    { accessor: 'quantity', Header: 'Miktar', width: 100, sortType: 'numeric', sortable: true, filterable: true, align: 'right' },
    { accessor: 'unit_price', Header: 'Birim Fiyat', width: 120, sortType: 'numeric', sortable: true, filterable: true, align: 'right' },
    { accessor: 'vat_percentage', Header: 'KDV Yüzde', width: 120, sortType: 'numeric', sortable: true, filterable: true, align: 'right' },
    { accessor: 'vat_amount', Header: 'KDV Tutar', width: 120, sortType: 'numeric', sortable: true, filterable: true, align: 'right' },
    { accessor: 'discount_rate', Header: 'İskonto Oran', width: 120, sortType: 'numeric', sortable: true, filterable: true, align: 'right' },
    { accessor: 'discount_amount', Header: 'İskontolu Tutar', width: 130, sortType: 'numeric', sortable: true, filterable: true, align: 'right' },
    { accessor: 'currency', Header: 'Döviz', width: 100, sortType: 'alphanumeric', sortable: true, filterable: true },
    { accessor: 'exchange_rate', Header: 'Kur', width: 100, sortType: 'numeric', sortable: true, filterable: true, align: 'right' },
    { accessor: 'currency_price', Header: 'Döviz Fiyat', width: 120, sortType: 'numeric', sortable: true, filterable: true, align: 'right' },
    { accessor: 'currency_movement_amount', Header: 'Döviz Hareket Tutar', width: 150, sortType: 'numeric', sortable: true, filterable: true, align: 'right' },
    { accessor: 'detail_description', Header: 'Detay Açıklama', width: 250, sortType: 'alphanumeric', sortable: true, filterable: true },
];



/**
 * Minimum arama karakteri sayısı
 */
export const MIN_SEARCH_LENGTH = 5;

/**
 * Hata mesajları
 */
export const ERROR_MESSAGES = {
    MIN_SEARCH_LENGTH: `Arama yapmak için en az ${MIN_SEARCH_LENGTH} karakter girilmelidir.`,
    YEAR_REQUIRED: 'Yıl seçimi zorunludur.',
    LOADING_ERROR: 'Veriler yüklenirken bir hata oluştu.',
    NO_DATA: 'Gösterilecek veri bulunamadı.'
};

/**
 * Durum mesajları
 */
export const STATUS_MESSAGES = {
    LOADING: 'Veriler yükleniyor...',
    NO_RESULTS: 'Sonuç bulunamadı.',
    SELECT_YEAR: 'Lütfen bir yıl seçin'
};

/**
 * Tablo sıralama yönleri
 */
export const SORT_DIRECTIONS = {
    ASC: 'asc',
    DESC: 'desc'
};
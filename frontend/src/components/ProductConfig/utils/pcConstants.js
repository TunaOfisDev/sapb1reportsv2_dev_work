// frontend/src/components/ProductConfig/utils/pcConstants.js

// API ve Routing için Base URL
const BASE_API_URL = process.env.REACT_APP_API_BASE_URL || ''; // Canlı ortamda /api gibi bir prefix olabilir

// API endpoint'leri
export const API_ENDPOINTS = {
    INITIAL_QUESTION: `${BASE_API_URL}/configuration/`, // İlk soru veya yapılandırmayı başlatma
    SUBMIT_ANSWER: `${BASE_API_URL}/configuration/`, // Cevap gönderme
    VARIANT_SUMMARY: (variantId) => `${BASE_API_URL}/configuration/${variantId}/`, // Varyant özet bilgisi
    VARIANT_REVERT: (variantId) => `${BASE_API_URL}/configuration/${variantId}/revert/`, // Geri dönüş işlemleri
    VARIANT_LIST: `${BASE_API_URL}/variants/`, // Varyant listesi
};

// Routing paths
export const ROUTES = {
    BASE: '/productconfig',
    CONFIGURATOR: '/productconfig/configurator',
    VARIANTS: '/productconfig/variants',
    VARIANT_DETAILS: '/productconfig/variants/:variantId', // Dinamik rota
};


// Soru tipleri
export const QUESTION_TYPES = {
    TEXT_INPUT: 'text_input',
    SINGLE_CHOICE: 'single_choice',
    MULTIPLE_CHOICE: 'multiple_choice',
    DATE_PICKER: 'date_picker',
    NUMBER_INPUT: 'number_input',
};

// Renk durumları
export const COLOR_STATUS = {
    BOTH: 'both',
    COLORED: 'colored',
    COLORLESS: 'colorless',
};

// Maksimum görüntülenecek seçenek sayısı
export const MAX_DISPLAYED_OPTIONS = 6;

// Varyant durumları
export const VARIANT_STATUS = {
    DRAFT: 'draft',
    COMPLETED: 'completed',
    SAVED: 'saved',
    ARCHIVED: 'archived',
};

// Hata mesajları
export const ERROR_MESSAGES = {
    FETCH_INITIAL_QUESTION: 'Başlangıç sorusu yüklenirken bir hata oluştu.',
    SUBMIT_ANSWER: 'Cevap gönderilirken bir hata oluştu.',
    FETCH_VARIANT_SUMMARY: 'Varyant özeti alınırken bir hata oluştu.',
    CREATE_VARIANT: 'Varyant oluşturulurken bir hata oluştu.',
    UPDATE_VARIANT: 'Varyant güncellenirken bir hata oluştu.',
    DELETE_VARIANT: 'Varyant silinirken bir hata oluştu.',
    FETCH_VARIANT_LIST: 'Varyant listesi alınırken bir hata oluştu.',
    FETCH_TAXONOMY_LIST: 'Taksonomi listesi alınırken bir hata oluştu.',
    NETWORK_ERROR: 'Ağ hatası. Lütfen bağlantınızı kontrol edin.',
    UNAUTHORIZED: 'Oturum süresi dolmuş. Lütfen tekrar giriş yapın.',
};

// Buton metinleri
export const BUTTON_TEXTS = {
    NEXT: 'İleri',
    BACK: 'Geri',
    SUBMIT: 'Gönder',
    SAVE: 'Kaydet',
    EDIT: 'Düzenle',
    CREATE_NEW: 'Yeni Oluştur',
    DELETE: 'Sil',
    CANCEL: 'İptal',
    CONFIRM: 'Onayla',
};

// Sayfa başlıkları
export const PAGE_TITLES = {
    HOME: 'Ürün Konfigüratörüne Hoş Geldiniz',
    CONFIGURATION: 'Ürün Konfigüratörü',
    VARIANT_SUMMARY: 'Varyant Özeti',
    VARIANT_LIST: 'Varyant Listesi',
    VARIANT_EDIT: 'Varyant Düzenle',
    TAXONOMY_MANAGEMENT: 'Taksonomi Yönetimi',
};

// Yerelleştirme ayarları
export const LOCALE_SETTINGS = {
    CURRENCY: 'tr-TR',
    DATE: 'tr-TR',
    NUMBER: 'tr-TR',
};

// Animasyon süreleri (milisaniye cinsinden)
export const ANIMATION_DURATIONS = {
    FADE: 300,
    SLIDE: 500,
    ZOOM: 400,
};

// Local Storage anahtarları
export const LOCAL_STORAGE_KEYS = {
    VARIANT_ID: 'pc_variant_id',
    PROJECT_NAME: 'pc_project_name',
    USER_PREFERENCES: 'pc_user_preferences',
    LAST_VISITED_PAGE: 'pc_last_visited_page',
};

// Validation kuralları
export const VALIDATION_RULES = {
    PROJECT_NAME_MIN_LENGTH: 3,
    PROJECT_NAME_MAX_LENGTH: 50,
    VARIANT_CODE_PATTERN: /^[A-Z0-9.-]+$/,
    PRICE_MIN: 0,
    PRICE_MAX: 1000000,
};

// UI teması renkleri
export const THEME_COLORS = {
    PRIMARY: '#007bff',
    SECONDARY: '#6c757d',
    SUCCESS: '#28a745',
    DANGER: '#dc3545',
    WARNING: '#ffc107',
    INFO: '#17a2b8',
    LIGHT: '#f8f9fa',
    DARK: '#343a40',
};

// Pagination ayarları
export const PAGINATION = {
    ITEMS_PER_PAGE: 10,
    MAX_PAGES_DISPLAYED: 5,
};

// Dosya yükleme limitleri
export const FILE_UPLOAD_LIMITS = {
    MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
    ALLOWED_FILE_TYPES: ['image/jpeg', 'image/png', 'application/pdf'],
};

// Zaman aşımı süreleri (milisaniye cinsinden)
export const TIMEOUTS = {
    API_REQUEST: 30000, // 30 saniye
    SESSION: 30 * 60 * 1000, // 30 dakika
};

// Koşul operatörleri
export const CONDITION_OPERATORS = {
    EQUALS: 'equals',
    NOT_EQUALS: 'not_equals',
    CONTAINS: 'contains',
    NOT_CONTAINS: 'not_contains',
    GREATER_THAN: 'greater_than',
    LESS_THAN: 'less_than',
};

// fiyat para birimi sabiti
export const CURRENCY = {
    CODE: 'EUR',
    SYMBOL: '€'
};
// path: frontend/src/components/formforgeapi/constants.js
/**
 * Genel sabitler - YENİ KURUMSAL YAPIYA UYGUN
 * ----------------------------------------------------------
 * •  Backend ile senkronize edilmiş tüm form alan tipleri (FIELD_TYPES)
 * •  Bu alanları gruplayan ve FieldPalette'i besleyen yapı (PALETTE_GROUPS)
 * •  Drag-and-Drop sabitleri ve yeni alan oluşturma şablonları
 * ----------------------------------------------------------
 */

// ==============================================================================
// 1. TEMEL SABİTLER (DEĞİŞİKLİK YOK)
// ==============================================================================

export const COLORS = {
  hanaBlue:     "#0A6ED1",
  hanaBlueDark: "#084C9B",
  hanaYellow:   "#F5B800",
  danger:       "#C0392B",
  lightGray:    "#dfe5e8",
};

export const DRAG_TYPES = {
  PALETTE_FIELD: "palette-field",
  CANVAS_FIELD:  "canvas-field",
};

// ==============================================================================
// 2. ALAN TİPLERİ VE GRUPLARI (TAMAMEN YENİLENDİ)
// ==============================================================================

// Backend `formfields.py` FieldTypes ile birebir aynı olmalı.
// Tüm alan tipleri için tek bir doğru kaynak.
export const FIELD_TYPES = {
    // Temel Alanlar
    TEXT: 'text',
    NUMBER: 'number',
    EMAIL: 'email',
    TEXTAREA: 'textarea',
    CHECKBOX: 'checkbox',
    PHONE: 'phone',
    URL: 'url',
    // Seçim Alanları
    SINGLE_SELECT: 'singleselect',
    MULTI_SELECT: 'multiselect',
    RADIO: 'radio',
    YES_NO: 'yesno',
    RATING: 'rating',
    // Tarih ve Zaman
    DATE: 'date',
    DATETIME: 'datetime',
    TIME: 'time',
    DATE_RANGE: 'daterange',
    // Gelişmiş Alanlar
    FILE_UPLOAD: 'fileupload',
    IMAGE_UPLOAD: 'imageupload',
    CURRENCY: 'currency',
    PERCENTAGE: 'percentage',
    SIGNATURE: 'signature',
    // Kurumsal Alanlar
    USER_PICKER: 'userpicker',
    DEPARTMENT_PICKER: 'departmentpicker',
    AUTOCOMPLETE: 'autocomplete',
    PREDEFINED_SELECT: 'predefined_select',
    // Yapısal Alanlar
    HEADING: 'heading',
    PARAGRAPH: 'paragraph',
    SEPARATOR: 'separator',
    // Özel Amaçlı Alanlar
    CALCULATED: 'calculated',
    HIDDEN: 'hidden',
};

// FieldPalette.jsx bileşenini doğrudan besleyecek olan ana yapı.
// Backend'deki FIELD_GROUPS'un frontend karşılığı.
export const PALETTE_GROUPS = [
    {
        id: 'basic',
        label: 'Temel Alanlar',
        items: [
            { type: FIELD_TYPES.TEXT,     label: 'Metin',           icon: 'T' },
            { type: FIELD_TYPES.NUMBER,   label: 'Sayı',            icon: '123' },
            { type: FIELD_TYPES.EMAIL,    label: 'E-posta',         icon: '@' },
            { type: FIELD_TYPES.TEXTAREA, label: 'Metin Alanı',     icon: '¶' },
            { type: FIELD_TYPES.CHECKBOX, label: 'Onay Kutusu',     icon: '☑' },
            { type: FIELD_TYPES.PHONE,    label: 'Telefon',         icon: '✆' },
            { type: FIELD_TYPES.URL,      label: 'Web Adresi',      icon: '🔗' },
        ]
    },
    {
        id: 'selection',
        label: 'Seçim Alanları',
        items: [
            { type: FIELD_TYPES.SINGLE_SELECT, label: 'Tekli Seçim',     icon: '▼' },
            { type: FIELD_TYPES.MULTI_SELECT,  label: 'Çoklu Seçim',     icon: '✔▼' },
            { type: FIELD_TYPES.RADIO,         label: 'Radyo Düğmesi',   icon: '◉' },
            { type: FIELD_TYPES.YES_NO,        label: 'Evet/Hayır',      icon: '✔/✖' },
            { type: FIELD_TYPES.RATING,        label: 'Derecelendirme',  icon: '★' },
        ]
    },
    {
        id: 'datetime',
        label: 'Tarih ve Zaman',
        items: [
            { type: FIELD_TYPES.DATE,       label: 'Tarih',           icon: '📅' },
            { type: FIELD_TYPES.DATETIME,   label: 'Tarih ve Saat',   icon: '🗓️' },
            { type: FIELD_TYPES.TIME,       label: 'Saat',            icon: '⏰' },
            { type: FIELD_TYPES.DATE_RANGE, label: 'Tarih Aralığı',   icon: '↔' },
        ]
    },
    {
        id: 'advanced',
        label: 'Gelişmiş Alanlar',
        items: [
            { type: FIELD_TYPES.FILE_UPLOAD,  label: 'Dosya Yükleme',    icon: '📎' },
            { type: FIELD_TYPES.IMAGE_UPLOAD, label: 'Resim Yükleme',    icon: '🖼️' },
            { type: FIELD_TYPES.CURRENCY,     label: 'Para Birimi',      icon: '₺' },
            { type: FIELD_TYPES.PERCENTAGE,   label: 'Yüzde',            icon: '%' },
            { type: FIELD_TYPES.SIGNATURE,    label: 'Elektronik İmza',  icon: '✍' },
        ]
    },
    {
        id: 'corporate',
        label: 'Kurumsal Alanlar',
        items: [
            { type: FIELD_TYPES.USER_PICKER,       label: 'Kullanıcı Seçimi',  icon: '👤' },
            { type: FIELD_TYPES.DEPARTMENT_PICKER, label: 'Departman Seçimi',  icon: '🏢' },
            { type: FIELD_TYPES.AUTOCOMPLETE,      label: 'Otomatik Tamamlama', icon: 'A…' },
        ]
    },
    {
        id: 'structural',
        label: 'Yapısal Alanlar',
        items: [
            { type: FIELD_TYPES.HEADING,   label: 'Başlık',          icon: 'H' },
            { type: FIELD_TYPES.PARAGRAPH, label: 'Açıklama Metni',  icon: 'p' },
            { type: FIELD_TYPES.SEPARATOR, label: 'Ayıraç',          icon: '—' },
        ]
    }
];


// ==============================================================================
// 3. YARDIMCI FONKSİYON VE ŞABLONLAR
// ==============================================================================

// Hangi alanların 'options' dizisine sahip olabileceğini belirten bir yardımcı.
export const FIELDS_WITH_OPTIONS = [ 
    FIELD_TYPES.SINGLE_SELECT,
    FIELD_TYPES.MULTI_SELECT,
    FIELD_TYPES.RADIO,
    FIELD_TYPES.AUTOCOMPLETE,
];

export const createEmptyField = ({ type = FIELD_TYPES.TEXT, order = 0 } = {}) => ({
  id: `temp_${Date.now()}`,
  label: "Yeni Alan",
  field_type: type,
  is_required: false,
  is_master: false,
  order,
  // GÜNCELLEME: Artık daha fazla alan tipi 'options' içerebilir.
  options: FIELDS_WITH_OPTIONS.includes(type) ? [] : undefined,
});

export const createEmptySection = (index = 0) => ({
  id: `section_${index}_${Date.now()}`,
  title: `Bölüm ${index + 1}`,
  rows: [
    { id: `row_${Date.now()}`, fields: [] },
  ],
});

// ==============================================================================
// 4. TÜM ALANLARI İÇEREN DÜZ LİSTE (DROPDOWN'LAR İÇİN)
// ==============================================================================

// PALETTE_GROUPS'taki tüm 'items' dizilerini birleştirip
// dropdown'ların ihtiyacı olan { value, label } formatına dönüştürür.
export const ALL_FIELD_OPTIONS = PALETTE_GROUPS.flatMap(group => 
    group.items.map(item => ({
        value: item.type,
        label: item.label,
    }))
);
# backend/formforgeapi/utils/formfields.py
from django.db import models
from django.utils.translation import gettext_lazy as _

class FieldTypes(models.TextChoices):
    """
    FormForgeAPI'de kullanılabilen tüm form alanı tipleri.
    Bu sınıf, FormField modelinde 'choices' olarak kullanılır.
    """
    # --- TEMEL ALANLAR ---
    TEXT = 'text', _('Metin')
    NUMBER = 'number', _('Sayı')
    EMAIL = 'email', _('E-posta')
    TEXTAREA = 'textarea', _('Metin Alanı')
    CHECKBOX = 'checkbox', _('Onay Kutusu')
    DATE = 'date', _('Tarih')
    PHONE = 'phone', _('Telefon Numarası')
    URL = 'url', _('Web Adresi (URL)')

    # --- SEÇİM ALANLARI ---
    SINGLE_SELECT = 'singleselect', _('Tekli Seçim')
    MULTI_SELECT = 'multiselect', _('Çoklu Seçim')
    RADIO = 'radio', _('Radyo Düğmesi')
    YES_NO = 'yesno', _('Evet/Hayır')
    
    # --- TARİH VE ZAMAN ALANLARI ---
    DATETIME = 'datetime', _('Tarih ve Saat')
    TIME = 'time', _('Saat')
    DATE_RANGE = 'daterange', _('Tarih Aralığı')

    # --- GELİŞMİŞ ALANLAR ---
    FILE_UPLOAD = 'fileupload', _('Dosya Yükleme')
    IMAGE_UPLOAD = 'imageupload', _('Resim Yükleme')
    CURRENCY = 'currency', _('Para Birimi')
    PERCENTAGE = 'percentage', _('Yüzde')
    RATING = 'rating', _('Derecelendirme')
    SIGNATURE = 'signature', _('Elektronik İmza')

    # --- KURUMSAL VE İŞLEVSEL ALANLAR ---
    USER_PICKER = 'userpicker', _('Kullanıcı Seçimi')
    DEPARTMENT_PICKER = 'departmentpicker', _('Departman Seçimi')
    AUTOCOMPLETE = 'autocomplete', _('Otomatik Tamamlama')
    PREDEFINED_SELECT = 'predefined_select', _('Ön Tanımlı Liste')

    # --- YAPISAL (GÖRSEL) ALANLAR ---
    HEADING = 'heading', _('Başlık')
    PARAGRAPH = 'paragraph', _('Açıklama Metni')
    SEPARATOR = 'separator', _('Ayıraç')
    
    # --- ÖZEL AMAÇLI ALANLAR ---
    CALCULATED = 'calculated', _('Hesaplanmış Alan')
    HIDDEN = 'hidden', _('Gizli Alan')

# Frontend'in palet oluşturmasını kolaylaştırmak için alanları gruplayan bir yapı (opsiyonel ama önerilir)
FIELD_GROUPS = {
    'basic': [
        FieldTypes.TEXT, FieldTypes.NUMBER, FieldTypes.EMAIL, FieldTypes.TEXTAREA,
        FieldTypes.CHECKBOX, FieldTypes.PHONE, FieldTypes.URL
    ],
    'selection': [
        FieldTypes.SINGLE_SELECT, FieldTypes.MULTI_SELECT, FieldTypes.RADIO, FieldTypes.YES_NO,
        FieldTypes.RATING
    ],
    'datetime': [
        FieldTypes.DATE, FieldTypes.DATETIME, FieldTypes.TIME, FieldTypes.DATE_RANGE
    ],
    'advanced': [
        FieldTypes.FILE_UPLOAD, FieldTypes.IMAGE_UPLOAD, FieldTypes.CURRENCY, 
        FieldTypes.PERCENTAGE, FieldTypes.SIGNATURE
    ],
    'corporate': [
        FieldTypes.USER_PICKER, FieldTypes.DEPARTMENT_PICKER, FieldTypes.AUTOCOMPLETE, 
        FieldTypes.PREDEFINED_SELECT
    ],
    'structural': [
        FieldTypes.HEADING, FieldTypes.PARAGRAPH, FieldTypes.SEPARATOR
    ],
    'special': [
        FieldTypes.CALCULATED, FieldTypes.HIDDEN
    ]
}

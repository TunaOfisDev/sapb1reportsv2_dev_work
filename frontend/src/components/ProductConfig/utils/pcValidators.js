// frontend/src/components/ProductConfig/utils/pcValidators.js
import { VALIDATION_RULES } from './pcConstants';

/**
 * Proje adını doğrular
 * @param {string} projectName - Doğrulanacak proje adı
 * @returns {string|null} Hata mesajı veya null (geçerli ise)
 */
export const validateProjectName = (projectName) => {
    if (!projectName || !projectName.trim()) {
        return 'Proje adı boş olamaz.';
    }
    if (projectName.length < VALIDATION_RULES.PROJECT_NAME_MIN_LENGTH) {
        return `Proje adı en az ${VALIDATION_RULES.PROJECT_NAME_MIN_LENGTH} karakter olmalıdır.`;
    }
    if (projectName.length > VALIDATION_RULES.PROJECT_NAME_MAX_LENGTH) {
        return `Proje adı en fazla ${VALIDATION_RULES.PROJECT_NAME_MAX_LENGTH} karakter olabilir.`;
    }
    return null;
};

/**
 * Seçilen seçenekleri doğrular
 * @param {number[]} selectedOptionIds - Seçilen seçenek ID'leri
 * @param {object} question - Soru nesnesi
 * @returns {string|null} Hata mesajı veya null (geçerli ise)
 */
export const validateSelectedOptions = (selectedOptionIds, question) => {
    if (question.is_required && (!selectedOptionIds || selectedOptionIds.length === 0)) {
        return 'Bu soru için en az bir seçenek seçmelisiniz.';
    }
    if (question.question_type === 'single_choice' && selectedOptionIds && selectedOptionIds.length > 1) {
        return 'Bu soru için sadece bir seçenek seçebilirsiniz.';
    }
    if (question.min_selections && selectedOptionIds && selectedOptionIds.length < question.min_selections) {
        return `En az ${question.min_selections} seçenek seçmelisiniz.`;
    }
    if (question.max_selections && selectedOptionIds && selectedOptionIds.length > question.max_selections) {
        return `En fazla ${question.max_selections} seçenek seçebilirsiniz.`;
    }
    return null;
};

/**
 * Metin cevabını doğrular
 * @param {string} textAnswer - Doğrulanacak metin cevabı
 * @param {object} question - Soru nesnesi
 * @returns {string|null} Hata mesajı veya null (geçerli ise)
 */
export const validateTextAnswer = (textAnswer, question) => {
    if (question.is_required && (!textAnswer || !textAnswer.trim())) {
        return 'Bu soru için bir cevap girmelisiniz.';
    }
    if (question.min_length && textAnswer && textAnswer.length < question.min_length) {
        return `Cevap en az ${question.min_length} karakter olmalıdır.`;
    }
    if (question.max_length && textAnswer && textAnswer.length > question.max_length) {
        return `Cevap en fazla ${question.max_length} karakter olabilir.`;
    }
    if (question.pattern && textAnswer && !new RegExp(question.pattern).test(textAnswer)) {
        return 'Cevap geçerli formatta değil.';
    }
    return null;
};

/**
 * Varyant ID'sini doğrular
 * @param {number|string} variantId - Doğrulanacak varyant ID'si
 * @returns {string|null} Hata mesajı veya null (geçerli ise)
 */
export const validateVariantId = (variantId) => {
    if (!variantId) {
        return 'Varyant ID\'si gereklidir.';
    }
    if (isNaN(Number(variantId)) || Number(variantId) <= 0) {
        return 'Geçersiz varyant ID\'si.';
    }
    return null;
};

/**
 * Fiyat değiştiricisini doğrular
 * @param {number} priceModifier - Doğrulanacak fiyat değiştiricisi
 * @returns {string|null} Hata mesajı veya null (geçerli ise)
 */
export const validatePriceModifier = (priceModifier) => {
    if (priceModifier === null || priceModifier === undefined || priceModifier === '') {
        return 'Fiyat değiştiricisi gereklidir.';
    }
    if (isNaN(Number(priceModifier))) {
        return 'Fiyat değiştiricisi bir sayı olmalıdır.';
    }
    if (Number(priceModifier) < VALIDATION_RULES.PRICE_MIN) {
        return `Fiyat değiştiricisi en az ${VALIDATION_RULES.PRICE_MIN} olmalıdır.`;
    }
    if (Number(priceModifier) > VALIDATION_RULES.PRICE_MAX) {
        return `Fiyat değiştiricisi en fazla ${VALIDATION_RULES.PRICE_MAX} olabilir.`;
    }
    return null;
};

/**
 * Renk durumunu doğrular
 * @param {string} colorStatus - Doğrulanacak renk durumu
 * @returns {string|null} Hata mesajı veya null (geçerli ise)
 */
export const validateColorStatus = (colorStatus) => {
    const validStatuses = ['colored', 'colorless', 'both'];
    if (!colorStatus || !validStatuses.includes(colorStatus)) {
        return 'Geçersiz renk durumu. Geçerli değerler: colored, colorless, both';
    }
    return null;
};

/**
 * Varyant kodunu doğrular
 * @param {string} variantCode - Doğrulanacak varyant kodu
 * @returns {string|null} Hata mesajı veya null (geçerli ise)
 */
export const validateVariantCode = (variantCode) => {
    if (!variantCode || !variantCode.trim()) {
        return 'Varyant kodu boş olamaz.';
    }
    if (!VALIDATION_RULES.VARIANT_CODE_PATTERN.test(variantCode)) {
        return 'Varyant kodu geçerli formatta değil. Sadece büyük harf, rakam, nokta ve tire içerebilir.';
    }
    return null;
};

/**
 * Tarih değerini doğrular
 * @param {string} date - Doğrulanacak tarih
 * @param {object} constraints - Tarih kısıtlamaları (min, max)
 * @returns {string|null} Hata mesajı veya null (geçerli ise)
 */
export const validateDate = (date, constraints = {}) => {
    const dateObj = new Date(date);
    if (isNaN(dateObj.getTime())) {
        return 'Geçersiz tarih formatı.';
    }
    if (constraints.min && dateObj < new Date(constraints.min)) {
        return `Tarih ${new Date(constraints.min).toLocaleDateString()} tarihinden sonra olmalıdır.`;
    }
    if (constraints.max && dateObj > new Date(constraints.max)) {
        return `Tarih ${new Date(constraints.max).toLocaleDateString()} tarihinden önce olmalıdır.`;
    }
    return null;
};

/**
 * Sayısal değeri doğrular
 * @param {number} value - Doğrulanacak sayısal değer
 * @param {object} constraints - Sayısal kısıtlamalar (min, max, integer)
 * @returns {string|null} Hata mesajı veya null (geçerli ise)
 */
export const validateNumericValue = (value, constraints = {}) => {
    if (value === null || value === undefined || value === '') {
        return 'Sayısal değer gereklidir.';
    }
    const numValue = Number(value);
    if (isNaN(numValue)) {
        return 'Geçerli bir sayı girilmelidir.';
    }
    if (constraints.integer && !Number.isInteger(numValue)) {
        return 'Tam sayı girilmelidir.';
    }
    if (constraints.min !== undefined && numValue < constraints.min) {
        return `Değer en az ${constraints.min} olmalıdır.`;
    }
    if (constraints.max !== undefined && numValue > constraints.max) {
        return `Değer en fazla ${constraints.max} olabilir.`;
    }
    return null;
};

/**
 * Sorunun cevabını doğrular
 * @param {any} answer - Kullanıcının verdiği cevap (text veya seçilen seçenekler)
 * @param {object} question - Soru nesnesi
 * @returns {string|null} Hata mesajı veya null (geçerli ise)
 */
export const validateQuestionAnswer = (answer, question) => {
    if (!question || !question.question_type) {
        return 'Geçersiz soru tanımı.';
    }

    // Metin cevapları için doğrulama
    if (question.question_type === 'text_input') {
        if (question.is_required && (!answer || !answer.trim())) {
            return 'Bu soru için bir cevap girmelisiniz.';
        }
        if (question.min_length && answer && answer.length < question.min_length) {
            return `Cevap en az ${question.min_length} karakter olmalıdır.`;
        }
        if (question.max_length && answer && answer.length > question.max_length) {
            return `Cevap en fazla ${question.max_length} karakter olabilir.`;
        }
        if (question.pattern && answer && !new RegExp(question.pattern).test(answer)) {
            return 'Cevap geçerli formatta değil.';
        }
        return null;
    }

    // Seçenekler için doğrulama
    if (['multiple_choice', 'single_choice'].includes(question.question_type)) {
        if (question.is_required && (!answer || answer.length === 0)) {
            return 'Bu soru için en az bir seçenek seçmelisiniz.';
        }
        if (question.question_type === 'single_choice' && answer && answer.length > 1) {
            return 'Bu soru için sadece bir seçenek seçebilirsiniz.';
        }
        if (question.min_selections && answer && answer.length < question.min_selections) {
            return `En az ${question.min_selections} seçenek seçmelisiniz.`;
        }
        if (question.max_selections && answer && answer.length > question.max_selections) {
            return `En fazla ${question.max_selections} seçenek seçebilirsiniz.`;
        }
        return null;
    }

    return 'Geçersiz soru tipi.';
};


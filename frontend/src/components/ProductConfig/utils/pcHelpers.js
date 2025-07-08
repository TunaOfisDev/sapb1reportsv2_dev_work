// frontend/src/components/ProductConfig/utils/pcHelpers.js
import { COLOR_STATUS, VALIDATION_RULES } from './pcConstants';

/**
 * Fiyatı formatlar
 * @param {number} price - Formatlanacak fiyat
 * @param {string} [currency='TRY'] - Para birimi
 * @returns {string} Formatlanmış fiyat
 */
export const formatPrice = (price, currencyConfig) => {
    if (!price) return '-';
    
    return new Intl.NumberFormat(currencyConfig.locale, {
        style: 'currency',
        currency: currencyConfig.code
    }).format(price);
};

/**
 * Tarihi formatlar
 * @param {string|Date} date - Formatlanacak tarih
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} Formatlanmış tarih
 */
export const formatDate = (date, options = {}) => {
    if (!date) return '-';
    
    const defaultOptions = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    try {
        return new Intl.DateTimeFormat(
            'tr-TR', 
            { ...defaultOptions, ...options }
        ).format(new Date(date));
    } catch (error) {
        console.error('Date formatting error:', error);
        return '-';
    }
};

/**
 * Varyant kodunu oluşturur
 * @param {object[]} selectedOptions - Seçilen seçenekler dizisi
 * @returns {string} Oluşturulan varyant kodu
 */
export const generateVariantCode = (selectedOptions) => {
    return selectedOptions
        .map(option => option.item_code)
        .filter(Boolean)
        .join('.');
};

/**
 * Seçenekleri renk durumuna göre filtreler
 * @param {object[]} options - Filtrelenecek seçenekler dizisi
 * @param {string} colorStatus - İstenen renk durumu
 * @returns {object[]} Filtrelenmiş seçenekler dizisi
 */
export const filterOptionsByColorStatus = (options, colorStatus) => {
    return options.filter(option => 
        option.color_status === COLOR_STATUS.BOTH || 
        option.color_status === colorStatus
    );
};

/**
 * Seçenekleri popülerliğe göre sıralar
 * @param {object[]} options - Sıralanacak seçenekler dizisi
 * @param {string} [order='desc'] - Sıralama yönü ('asc' veya 'desc')
 * @returns {object[]} Sıralanmış seçenekler dizisi
 */
export const sortOptionsByPopularity = (options, order = 'desc') => {
    return [...options].sort((a, b) => {
        const comparison = b.popularity - a.popularity;
        return order === 'asc' ? -comparison : comparison;
    });
};

/**
 * Seçenekleri ada göre arar
 * @param {object[]} options - Aranacak seçenekler dizisi
 * @param {string} searchTerm - Arama terimi
 * @returns {object[]} Filtrelenmiş seçenekler dizisi
 */
export const searchOptionsByName = (options, searchTerm) => {
    const lowerCaseSearchTerm = searchTerm.toLowerCase();
    return options.filter(option => 
        option.name.toLowerCase().includes(lowerCaseSearchTerm)
    );
};

/**
 * Seçenek ID'lerini seçenek nesnelerine dönüştürür
 * @param {number[]} optionIds - Seçenek ID'leri dizisi
 * @param {object[]} allOptions - Tüm seçenekler dizisi
 * @returns {object[]} Seçenek nesneleri dizisi
 */
export const mapOptionIdsToObjects = (optionIds, allOptions) => {
    return optionIds.map(id => allOptions.find(option => option.id === id)).filter(Boolean);
};

/**
 * Toplam fiyatı hesaplar
 * @param {object[]} selectedOptions - Seçilen seçenekler dizisi
 * @returns {number} Toplam fiyat
 */
export const calculateTotalPrice = (selectedOptions) => {
    return selectedOptions.reduce((total, option) => total + (parseFloat(option.price_modifier) || 0), 0);
};

/**
 * Varyant açıklamasını oluşturur
 * @param {object[]} selectedOptions - Seçilen seçenekler dizisi
 * @returns {string} Oluşturulan varyant açıklaması
 */
export const generateVariantDescription = (selectedOptions) => {
    return selectedOptions
        .map(option => option.name)
        .join(', ');
};

/**
 * Proje adının geçerliliğini kontrol eder
 * @param {string} projectName - Kontrol edilecek proje adı
 * @returns {boolean} Geçerlilik durumu
 */
export const isValidProjectName = (projectName) => {
    return projectName.length >= VALIDATION_RULES.PROJECT_NAME_MIN_LENGTH &&
           projectName.length <= VALIDATION_RULES.PROJECT_NAME_MAX_LENGTH;
};

/**
 * Varyant kodunun geçerliliğini kontrol eder
 * @param {string} variantCode - Kontrol edilecek varyant kodu
 * @returns {boolean} Geçerlilik durumu
 */
export const isValidVariantCode = (variantCode) => {
    return VALIDATION_RULES.VARIANT_CODE_PATTERN.test(variantCode);
};

/**
 * Fiyatın geçerliliğini kontrol eder
 * @param {number} price - Kontrol edilecek fiyat
 * @returns {boolean} Geçerlilik durumu
 */
export const isValidPrice = (price) => {
    return price >= VALIDATION_RULES.PRICE_MIN && price <= VALIDATION_RULES.PRICE_MAX;
};

/**
 * Koşullu soruları değerlendirir
 * @param {object[]} conditionalQuestions - Koşullu sorular dizisi
 * @param {object} userAnswers - Kullanıcı cevapları
 * @returns {object[]} Gösterilmesi gereken sorular dizisi
 */
export const evaluateConditionalQuestions = (conditionalQuestions, userAnswers) => {
    return conditionalQuestions.filter(question => {
        const { condition } = question;
        const userAnswer = userAnswers[condition.trigger_question_id];

        switch (condition.operator) {
            case 'equals':
                return condition.trigger_options.includes(userAnswer);
            case 'not_equals':
                return !condition.trigger_options.includes(userAnswer);
            // Diğer operatörler için ek kontroller eklenebilir
            default:
                return false;
        }
    });
};

/**
 * Taksonomi ağacını oluşturur
 * @param {object[]} taxonomies - Düz taksonomi listesi
 * @returns {object} Hiyerarşik taksonomi ağacı
 */
export const buildTaxonomyTree = (taxonomies) => {
    const tree = {};
    const lookup = {};

    taxonomies.forEach(tax => {
        lookup[tax.id] = { ...tax, children: [] };
    });

    taxonomies.forEach(tax => {
        if (tax.parent) {
            lookup[tax.parent].children.push(lookup[tax.id]);
        } else {
            tree[tax.id] = lookup[tax.id];
        }
    });

    return tree;
};

/**
 * Belirli bir derinliğe kadar olan alt taksonomileri getirir
 * @param {object} taxonomy - Kök taksonomi
 * @param {number} depth - İstenen derinlik
 * @returns {object[]} Alt taksonomiler dizisi
 */
export const getDescendantTaxonomies = (taxonomy, depth = Infinity) => {
    const descendants = [];
    const queue = [[taxonomy, 0]];

    while (queue.length > 0) {
        const [currentTax, currentDepth] = queue.shift();

        if (currentDepth > 0) {
            descendants.push(currentTax);
        }

        if (currentDepth < depth) {
            currentTax.children.forEach(child => {
                queue.push([child, currentDepth + 1]);
            });
        }
    }

    return descendants;
};


export const mapQuestionType = (questionType) => {
    if (questionType === 'choice') {
        return 'single_choice';
    }
    return questionType;
};

export const combineOptions = (options) => {
    console.log('Options before combining:', options); // Log ekleyelim
    if (Array.isArray(options)) {
        return options;
    } else if (options && typeof options === 'object') {
        const combined = [...(options.popular_options || []), ...(options.other_options || [])];
        console.log('Combined options:', combined); // Log ekleyelim
        return combined;
    } else {
        console.warn('Unexpected options format:', options);
        return [];
    }
};
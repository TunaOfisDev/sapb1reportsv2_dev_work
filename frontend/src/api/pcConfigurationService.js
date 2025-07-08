// frontend/src/api/pcConfigurationService.js
import axiosInstance from './axiosconfig';
import pcLogger from '../components/ProductConfig/utils/pcLogger';

// Backend'den gelen veri dönüşümleri
const transformQuestionType = (backendType) => {
    const typeMapping = {
        'text_input': 'text_input',
        'multiple_choice': 'multiple_choice',
        'choice': 'single_choice'
    };
    return typeMapping[backendType] || 'text_input';
};

const transformQuestion = (questionData) => {
    if (!questionData) return null;

    return {
        id: questionData.id,
        name: questionData.text,
        question_type: transformQuestionType(questionData.type),
        is_required: questionData.is_required,
        help_text: questionData.help_text,
        category_type: questionData.category_type,
        is_visible: questionData.is_visible,
        dependent_rules: questionData.dependent_rules || [],
        options: questionData.options?.map(opt => ({
            id: opt.id,
            name: opt.name,
            option_type: opt.option_type,
            image_url: opt.image_url,
            final_price: parseFloat(opt.final_price), 
            normal_price: parseFloat(opt.normal_price),
            price_melamine: parseFloat(opt.price_melamine),
            price_laminate: parseFloat(opt.price_laminate),
            price_veneer: parseFloat(opt.price_veneer),
            price_lacquer: parseFloat(opt.price_lacquer),
            melamine_triggers: opt.melamine_triggers || [],
            laminate_triggers: opt.laminate_triggers || [],
            veneer_triggers: opt.veneer_triggers || [],
            lacquer_triggers: opt.lacquer_triggers || [],
            is_trigger: opt.is_trigger || false,
            applicable_brands: opt.applicable_brands || [],
            applicable_groups: opt.applicable_groups || [],
            applicable_categories: opt.applicable_categories || [],
            applicable_product_models: opt.applicable_product_models || []
        })) || []
    };
};


const transformDependentRules = (rules) => {
    return rules.map(rule => ({
        id: rule.id,
        rule_type: rule.rule_type,
        trigger_option_id: rule.trigger_option,
        dependent_questions: rule.dependent_questions || []
    }));
};


const transformVariantInfo = (variantInfo) => {
    if (!variantInfo) return null;

    const oldComponentCodes = Array.isArray(variantInfo.old_component_codes)
        ? variantInfo.old_component_codes
        : variantInfo.old_component_codes.split(", ");

    return {
        id: variantInfo.id,
        project_name: variantInfo.project_name,
        variant_code: variantInfo.variant_code,
        variant_description: variantInfo.variant_description,
        total_price: variantInfo.total_price,
        status: variantInfo.status,
        old_component_codes: oldComponentCodes
    };
};


// Answer değerini backend'in beklediği formata dönüştürür
const transformAnswer = (answer, questionType) => {
    if (questionType === 'text_input') {
        return answer;
    }
    // Eğer answer bir array ise ilk elemanı al
    if (Array.isArray(answer)) {
        return answer[0];
    }
    return answer;
};

const pcConfigurationService = {
    // İlk soruyu alma
    getInitialQuestion: async () => {
        try {
            const response = await axiosInstance.get('productconfig/configuration/');
            pcLogger.log('Initial Question Response:', response.data);
            
            return {
                next_question: transformQuestion(response.data.question),
                message: response.data.message
            };
        } catch (error) {
            pcLogger.error('Error fetching initial question:', error);
            throw error;
        }
    },

    // Yanıt gönderme
    saveAnswer: async (data) => {
        try {
            const requestData = {
                variant_id: data.variant_id || null,
                question_id: data.question_id,
                answer: transformAnswer(data.answer, data.question_type)
            };
            
            pcLogger.log('Sending request data:', requestData);
            const response = await axiosInstance.post('productconfig/configuration/', requestData);
            pcLogger.log('Save Answer Response:', response.data);
            pcLogger.log('Variant Info with Old Component Codes:', response.data.variant_info);
            
            // Variant bilgilerini dönüştür ve old_component_codes ekle
            const transformedVariantInfo = {
                ...transformVariantInfo(response.data.variant_info),
                old_component_codes: response.data.variant_info?.old_component_codes || []
            };

            pcLogger.log('Transformed Variant Info:', transformedVariantInfo);
            
            return {
                variant_id: response.data.variant_id,
                variant_info: transformedVariantInfo, // Güncellenmiş varyant bilgisi
                next_question: transformQuestion(response.data.question),
                dependent_rules: transformDependentRules(response.data.dependent_rules || []),
                visible_questions: response.data.visible_questions || [],
                is_completed: response.data.is_completed, 
                is_complete: !!response.data.detail?.includes('tamamlandı')
            };
        } catch (error) {
            pcLogger.error('Error saving answer:', error);
            throw error;
        }
    },

    // Varyant silme
    deleteVariant: async (variantId) => {
        try {
            const response = await axiosInstance.delete(`productconfig/configuration/${variantId}/`);
            return response.data;
        } catch (error) {
            pcLogger.error('Error deleting variant:', error);
            throw error;
        }
    },

    // Önceki soruya dönme
    revertToPreviousQuestion: async (variantId) => {
        try {
            const response = await axiosInstance.put(`productconfig/configuration/${variantId}/revert/`);
            pcLogger.log('Revert Response:', response.data);
            
            return {
                variant_id: response.data.variant_id,
                variant_info: transformVariantInfo(response.data.variant_info),
                question: transformQuestion(response.data.question),
                is_completed: response.data.is_completed
            };
        } catch (error) {
            pcLogger.error('Error reverting to previous question:', error);
            throw error;
        }
    },

    // Varyant özeti alma
    getVariantSummary: async (variantId) => {
        try {
            const response = await axiosInstance.get(`productconfig/configuration/${variantId}/`);
            pcLogger.log('Variant Summary Response:', response.data);
            
            return {
                ...transformVariantInfo(response.data.variant_info),
                previous_answers: response.data.previous_answers,
                current_question: transformQuestion(response.data.current_question),
                old_component_codes: response.data.variant_info.old_component_codes || [],
                is_completed: response.data.is_completed
            };
        } catch (error) {
            pcLogger.error('Error fetching variant summary:', error);
            throw error;
        }
    },

    // Varyant listesi getirme
    getVariantList: async (filters = {}) => {
        try {
            // Query parametrelerini oluştur
            const queryParams = new URLSearchParams();
            if (filters.brand_id) queryParams.append('brand_id', filters.brand_id);
            if (filters.category_id) queryParams.append('category_id', filters.category_id);
            if (filters.product_model_id) queryParams.append('product_model_id', filters.product_model_id);
            if (filters.status) queryParams.append('status', filters.status);

            const response = await axiosInstance.get(`productconfig/variants/?${queryParams.toString()}`);
            pcLogger.log('Variant List Response:', response.data);
            
            return {
                variants: response.data.variants,
                total_count: response.data.total_count
            };
        } catch (error) {
            pcLogger.error('Error fetching variant list:', error);
            throw error;
        }
    }
};

export default pcConfigurationService;

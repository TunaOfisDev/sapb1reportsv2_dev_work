// frontend/src/components/ProductConfig/configuration/PCQuestionCard.js
import React, { useState, useCallback, useEffect, useMemo } from 'react';
import PropTypes from 'prop-types';
import PCButton from '../common/PCButton';
import PCForwardButton from '../common/PCForwardButton';
import PCInput from '../common/PCInput';
import PCOptionList from './PCOptionList';
import PCLoadingTransition from '../common/PCLoadingTransition';
import { validateQuestionAnswer } from '../utils/pcValidators';
import '../css/PCQuestionCard.css';

const PCQuestionCard = ({
    question,
    options = [],
    onAnswer,
    onBack,
    currentAnswer = null,
    currency = 'EUR',
    dependentRules = [],
    isVisible = true,
    visibleQuestions = [],
    variantId,
    onDeleteAndReset,
    isFirstQuestion,
}) => {
    const [state, setState] = useState({
        textAnswer: '',
        selectedOptions: [],
        error: null,
        isLoading: false, // Yükleme durumu
    });
    

    const updateState = useCallback((updates) => {
        setState((prev) => ({ ...prev, ...updates }));
    }, []);

    // Yeni bir soru geldiğinde state'i sıfırla
    useEffect(() => {
        setState({
            textAnswer: '',
            selectedOptions: [],
            error: null,
            isLoading: false,
        });
    }, [question.id]); // question.id değiştiğinde tetiklenir

    // İleri butonunun aktif/pasif kontrolü
    const isNextDisabled = useMemo(() => {
        if (!question || !question.question_type) return true; // Soru yoksa buton pasif
        if (question.question_type === 'text_input') {
            return !state.textAnswer.trim(); // Text input için boş kontrolü
        }
        if (question.question_type === 'single_choice' || question.question_type === 'multiple_choice') {
            return state.selectedOptions.length === 0; // Seçenek seçilmemişse buton pasif
        }
        return false; // Varsayılan olarak buton aktif
    }, [question, state.textAnswer, state.selectedOptions]);

    // Seçenek seçimi
    const handleOptionSelect = useCallback((selected) => {
        updateState({ 
            selectedOptions: Array.isArray(selected) ? selected : [selected],
            error: null 
        });
    }, [updateState]);

    // Yanıt gönderimi
    const handleSubmit = useCallback(
        async (e) => {
            e.preventDefault();
            updateState({ isLoading: true });

            const answer = question.question_type === 'text_input' ? state.textAnswer : state.selectedOptions;
            const validationError = validateQuestionAnswer(answer, question);

            if (validationError) {
                updateState({ error: validationError, isLoading: false });
                return;
            }

            await onAnswer(answer);
            updateState({ isLoading: false });
        },
        [question, state.textAnswer, state.selectedOptions, onAnswer, updateState]
    );

    if (!isVisible) return null;

    return (
        <div className="pc-question-card">
            {/* Sabit başlık */}
            <div className="pc-question-card__header">
                <h2 className="pc-question-card__title">{question.name}</h2>
                {question.description && <p className="pc-question-card__description">{question.description}</p>}
            </div>

            {/* PCLoadingTransition sadece içerik için */}
            <PCLoadingTransition isLoading={state.isLoading}>
                <div className="pc-question-card__content">
                    {question.question_type === 'text_input' ? (
                        <form onSubmit={handleSubmit} className="pc-question-card__form">
                            <PCInput
                                type="text"
                                name="text_answer"
                                value={state.textAnswer}
                                onChange={(e) => updateState({ textAnswer: e.target.value, error: null })}
                                placeholder="Cevabınızı buraya yazın"
                                required={question.is_required}
                                error={state.error}
                            />
                        </form>
                    ) : (
                        <div className="pc-question-card__options">
                            <PCOptionList
                                options={options}
                                onSelect={handleOptionSelect} // Seçim işlevini kullan
                                initialSelectedOptions={[]} // Her zaman boş array ile başla
                                currency={currency}
                            />
                            {state.error && <p className="pc-question-card__error">{state.error}</p>}
                        </div>
                    )}
                </div>
            </PCLoadingTransition>

            {/* Sabit butonlar */}
            <div className="pc-question-card__actions">
                {variantId && (
                    <PCButton onClick={onDeleteAndReset} variant="danger" size="medium">
                        Sil ve Yeni Oluştur
                    </PCButton>
                )}
                <PCForwardButton
                    isLoading={state.isLoading}
                    onClick={handleSubmit}
                    disabled={isNextDisabled || state.isLoading} // Disabled durumu
                >
                    İleri
                </PCForwardButton>
            </div>
        </div>
    );
};

PCQuestionCard.propTypes = {
    question: PropTypes.shape({
        id: PropTypes.number.isRequired,
        name: PropTypes.string.isRequired,
        description: PropTypes.string,
        question_type: PropTypes.oneOf(['text_input', 'multiple_choice', 'single_choice']).isRequired,
        is_required: PropTypes.bool.isRequired,
        is_conditional: PropTypes.bool,
        max_selections: PropTypes.number,
    }).isRequired,
    options: PropTypes.arrayOf(PropTypes.object),
    onAnswer: PropTypes.func.isRequired,
    currentAnswer: PropTypes.oneOfType([PropTypes.string, PropTypes.array]),
    currency: PropTypes.string,
    dependentRules: PropTypes.array,
    isVisible: PropTypes.bool,
    visibleQuestions: PropTypes.array,
    variantId: PropTypes.number,
    onDeleteAndReset: PropTypes.func,
    isFirstQuestion: PropTypes.bool,
};

export default PCQuestionCard;
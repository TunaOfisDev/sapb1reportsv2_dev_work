// frontend/src/components/ProductConfig/store/pcConfigurationSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import pcConfigurationService from '../../../api/pcConfigurationService';

// Async thunks
export const fetchNextQuestion = createAsyncThunk(
  'pcConfiguration/fetchNextQuestion',
  async ({ currentQuestionId, variantId, taxonomies }, { rejectWithValue }) => {
    try {
      const response = await pcConfigurationService.getNextQuestion(currentQuestionId, variantId, taxonomies);
      return response.data; // Yanıtın data kısmını döndürdüğünüzden emin olun
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

export const saveAnswer = createAsyncThunk(
  'pcConfiguration/saveAnswer',
  async (answerData, { rejectWithValue }) => {
    try {
      const response = await pcConfigurationService.saveAnswer(answerData);
      return response.data; // Yanıtın data kısmını döndürdüğünüzden emin olun
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

// Initial state
const initialState = {
  currentQuestion: null,
  options: [],
  variantId: null,
  projectName: '',
  variantSummary: {
    variantCode: '',
    variantDescription: '',
    totalPrice: 0,
  },
  configurationHistory: [],
  conditionalQuestions: [],
  taxonomies: [],
  loading: false,
  error: null,
  lastAnswer: null,
  isCompleted: false,

  // Yeni eklenen state'ler
  isUpdating: false, // Güncelleme durumu
  updatingMessage: '', // Güncelleme mesajı
};

// Create slice
const pcConfigurationSlice = createSlice({
  name: 'pcConfiguration',
  initialState,
  reducers: {
    setCurrentQuestion: (state, action) => {
      state.currentQuestion = action.payload;
    },
    setOptions: (state, action) => {
      state.options = action.payload;
    },
    setVariantId: (state, action) => {
      state.variantId = action.payload;
    },
    setProjectName: (state, action) => {
      state.projectName = action.payload;
    },
    updateVariantSummary: (state, action) => {
      state.variantSummary = {
        ...state.variantSummary,
        ...action.payload,
      };
    },
    addToHistory: (state, action) => {
      state.configurationHistory.push(action.payload);
    },
    removeLastFromHistory: (state) => {
      state.configurationHistory.pop();
    },
    setConditionalQuestions: (state, action) => {
      state.conditionalQuestions = action.payload;
    },
    setTaxonomies: (state, action) => {
      state.taxonomies = action.payload;
    },
    setLastAnswer: (state, action) => {
      state.lastAnswer = action.payload;
    },
    resetConfiguration: () => initialState,
  },
  extraReducers: (builder) => {
    builder
      // fetchNextQuestion Thunk
      .addCase(fetchNextQuestion.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchNextQuestion.fulfilled, (state, action) => {
        state.loading = false;
        state.currentQuestion = action.payload.next_question;
        state.options = action.payload.options || [];
        state.variantId = action.payload.variant_id;
        state.projectName = action.payload.project_name || '';
        state.variantSummary = {
          variantCode: action.payload.variant_code || '',
          variantDescription: action.payload.variant_description || '',
          totalPrice: action.payload.total_price || 0,
        };
        state.conditionalQuestions = action.payload.conditional_questions || [];
        state.taxonomies = action.payload.taxonomies || [];

        // Eğer next_question null ise, tamamlandığını işaretle
        if (!action.payload.next_question) {
          state.isCompleted = true;
        }
      })
      .addCase(fetchNextQuestion.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Bir hata oluştu';
      })

      // saveAnswer Thunk
      .addCase(saveAnswer.pending, (state) => {
        state.isUpdating = true;
        state.updatingMessage = 'Sonraki Soru ve Seçenekler Yükleniyor...';
        state.error = null;
      })
      .addCase(saveAnswer.fulfilled, (state, action) => {
        state.isUpdating = false;
        state.updatingMessage = '';
        state.currentQuestion = action.payload.next_question;
        state.options = action.payload.options || [];
        state.variantId = action.payload.variant_id;
        state.projectName = action.payload.project_name || '';
        state.variantSummary = {
          variantCode: action.payload.variant_code || '',
          variantDescription: action.payload.variant_description || '',
          totalPrice: action.payload.total_price || 0,
        };
        state.conditionalQuestions = action.payload.conditional_questions || [];
        state.taxonomies = action.payload.taxonomies || [];

        // Kullanıcı cevabı ve soruyu geçmişe ekleyin
        state.configurationHistory.push({
          question: state.currentQuestion,
          answer: state.lastAnswer,
        });

        // Eğer next_question null ise, tamamlandığını işaretle
        if (!action.payload.next_question) {
          state.isCompleted = true;
        }
      })
      .addCase(saveAnswer.rejected, (state, action) => {
        state.isUpdating = false;
        state.updatingMessage = '';
        state.error = action.payload || 'Cevap gönderilirken bir hata oluştu';
      });
  },
});

// Export actions
export const {
  setCurrentQuestion,
  setOptions,
  setVariantId,
  setProjectName,
  updateVariantSummary,
  addToHistory,
  removeLastFromHistory,
  setConditionalQuestions,
  setTaxonomies,
  setLastAnswer,
  resetConfiguration,
} = pcConfigurationSlice.actions;

// Selectors
export const selectCurrentQuestion = (state) => state.pcConfiguration.currentQuestion;
export const selectOptions = (state) => state.pcConfiguration.options;
export const selectVariantId = (state) => state.pcConfiguration.variantId;
export const selectProjectName = (state) => state.pcConfiguration.projectName;
export const selectVariantSummary = (state) => state.pcConfiguration.variantSummary;
export const selectConfigurationHistory = (state) => state.pcConfiguration.configurationHistory;
export const selectConditionalQuestions = (state) => state.pcConfiguration.conditionalQuestions;
export const selectTaxonomies = (state) => state.pcConfiguration.taxonomies;
export const selectLoading = (state) => state.pcConfiguration.loading;
export const selectError = (state) => state.pcConfiguration.error;
export const selectLastAnswer = (state) => state.pcConfiguration.lastAnswer;
export const selectIsCompleted = (state) => state.pcConfiguration.isCompleted;

// Yeni eklenen selectorlar
export const selectIsUpdating = (state) => state.pcConfiguration.isUpdating;
export const selectUpdatingMessage = (state) => state.pcConfiguration.updatingMessage;

export default pcConfigurationSlice.reducer;

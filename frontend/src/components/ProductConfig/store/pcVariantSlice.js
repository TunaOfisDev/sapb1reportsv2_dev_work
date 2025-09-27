// frontend/src/components/ProductConfig/store/pcVariantSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import pcConfigurationService from '../../../api/pcConfigurationService';

// Async Thunks
export const fetchVariantDetails = createAsyncThunk(
    'pcVariant/fetchVariantDetails',
    async (variantId, { rejectWithValue }) => {
        try {
            const response = await pcConfigurationService.getVariantSummary(variantId);
            return response;
        } catch (err) {
            return rejectWithValue(err.response?.data || 'Varyant detayları alınamadı');
        }
    }
);

export const fetchVariantList = createAsyncThunk(
    'pcVariant/fetchVariantList',
    async (_, { rejectWithValue }) => {
        try {
            const response = await pcConfigurationService.getVariantList();
            // API'den gelen variants dizisini direkt dön
            return response.variants || [];
        } catch (err) {
            return rejectWithValue(err.response?.data || 'Varyant listesi alınamadı');
        }
    }
);

export const createVariant = createAsyncThunk(
    'pcVariant/createVariant',
    async (variantData, { rejectWithValue }) => {
        try {
            const response = await pcConfigurationService.createVariant(variantData);
            return response;
        } catch (err) {
            return rejectWithValue(err.response?.data || 'Varyant oluşturulamadı');
        }
    }
);

export const updateVariantDetails = createAsyncThunk(
    'pcVariant/updateVariantDetails',
    async ({ variantId, updateData }, { rejectWithValue }) => {
        try {
            const response = await pcConfigurationService.updateVariant(variantId, updateData);
            return response;
        } catch (err) {
            return rejectWithValue(err.response?.data || 'Varyant güncellenemedi');
        }
    }
);

export const deleteVariant = createAsyncThunk(
    'pcVariant/deleteVariant',
    async (variantId, { rejectWithValue }) => {
        try {
            await pcConfigurationService.deleteVariant(variantId);
            return variantId;
        } catch (err) {
            return rejectWithValue(err.response?.data || 'Varyant silinemedi');
        }
    }
);

// Initial State
const initialState = {
    currentVariant: null,
    variantList: [],
    loading: false,
    error: null,
    lastUpdated: null,
};

// Slice
export const pcVariantSlice = createSlice({
    name: 'pcVariant',
    initialState,
    reducers: {
        setCurrentVariant: (state, action) => {
            state.currentVariant = action.payload;
        },
        clearCurrentVariant: (state) => {
            state.currentVariant = null;
            state.error = null;
        },
        clearVariants: (state) => {
            state.variantList = [];
        },
        clearError: (state) => {
            state.error = null;
        },
    },
    extraReducers: (builder) => {
        builder
            // Varyant Detayları
            .addCase(fetchVariantDetails.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchVariantDetails.fulfilled, (state, action) => {
                state.loading = false;
                state.currentVariant = action.payload;
                state.lastUpdated = new Date().toISOString();
            })
            .addCase(fetchVariantDetails.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })

            // Varyant Listesi
            .addCase(fetchVariantList.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchVariantList.fulfilled, (state, action) => {
                state.loading = false;
                state.variantList = Array.isArray(action.payload) ? action.payload : [];
                state.lastUpdated = new Date().toISOString();
            })
            .addCase(fetchVariantList.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
                state.variantList = []; // Hata durumunda boş liste
            })

            // Varyant Oluşturma
            .addCase(createVariant.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(createVariant.fulfilled, (state, action) => {
                state.loading = false;
                state.variantList.push(action.payload);
                state.currentVariant = action.payload;
                state.lastUpdated = new Date().toISOString();
            })
            .addCase(createVariant.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })

            // Varyant Güncelleme
            .addCase(updateVariantDetails.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(updateVariantDetails.fulfilled, (state, action) => {
                state.loading = false;
                // Listedeki varyantı güncelle
                const index = state.variantList.findIndex(v => v.id === action.payload.id);
                if (index !== -1) {
                    state.variantList[index] = action.payload;
                }
                // Mevcut varyant ise onu da güncelle
                if (state.currentVariant && state.currentVariant.id === action.payload.id) {
                    state.currentVariant = action.payload;
                }
                state.lastUpdated = new Date().toISOString();
            })
            .addCase(updateVariantDetails.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })

            // Varyant Silme
            .addCase(deleteVariant.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(deleteVariant.fulfilled, (state, action) => {
                state.loading = false;
                state.variantList = state.variantList.filter(v => v.id !== action.payload);
                if (state.currentVariant && state.currentVariant.id === action.payload) {
                    state.currentVariant = null;
                }
                state.lastUpdated = new Date().toISOString();
            })
            .addCase(deleteVariant.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            });
    },
});

// Actions
export const {
    setCurrentVariant,
    clearCurrentVariant,
    clearVariants,
    clearError,
} = pcVariantSlice.actions;

// Selectors
export const selectCurrentVariant = (state) => state.pcVariant.currentVariant;
export const selectVariantList = (state) => state.pcVariant.variantList;
export const selectVariantLoading = (state) => state.pcVariant.loading;
export const selectVariantError = (state) => state.pcVariant.error;
export const selectLastUpdated = (state) => state.pcVariant.lastUpdated;

export default pcVariantSlice.reducer;
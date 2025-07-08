// frontend/src/components/ProductConfig/store/pcSettingsSlice.js
import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    currency: {
        code: 'EUR',
        symbol: '€',
        locale: 'tr-TR'
    },
    // İleride başka global ayarlar da buraya eklenebilir
};

const pcSettingsSlice = createSlice({
    name: 'pcSettings',
    initialState,
    reducers: {
        updateCurrency: (state, action) => {
            state.currency = { ...state.currency, ...action.payload };
        }
    }
});

export const { updateCurrency } = pcSettingsSlice.actions;
export const selectCurrency = (state) => state.pcSettings.currency;
export default pcSettingsSlice.reducer;
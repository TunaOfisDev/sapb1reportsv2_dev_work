// frontend/src/components/ProductConfig/store/pcTaxonomySlice.js
import { createSlice } from '@reduxjs/toolkit';

const pcTaxonomySlice = createSlice({
  name: 'pcTaxonomy',
  initialState: {
    taxonomies: [],
    loading: false,
    error: null,
  },
  reducers: {
    setTaxonomies: (state, action) => {
      state.taxonomies = action.payload;
    },
    setTaxonomyLoading: (state, action) => {
      state.loading = action.payload;
    },
    setTaxonomyError: (state, action) => {
      state.error = action.payload;
    },
  },
});

export const { setTaxonomies, setTaxonomyLoading, setTaxonomyError } = pcTaxonomySlice.actions;

export default pcTaxonomySlice.reducer;
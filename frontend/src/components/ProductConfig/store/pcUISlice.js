// frontend/src/components/ProductConfig/store/pcUISlice.js
import { createSlice } from '@reduxjs/toolkit';

const pcUISlice = createSlice({
  name: 'pcUI',
  initialState: {
    modalOpen: false,
    currentModal: null,
    loading: false,
    notifications: [],
  },
  reducers: {
    setModalOpen: (state, action) => {
      state.modalOpen = action.payload;
    },
    setCurrentModal: (state, action) => {
      state.currentModal = action.payload;
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    addNotification: (state, action) => {
      state.notifications.push(action.payload);
    },
    removeNotification: (state, action) => {
      state.notifications = state.notifications.filter(n => n.id !== action.payload);
    },
  },
});

export const { 
  setModalOpen, 
  setCurrentModal, 
  setLoading, 
  addNotification, 
  removeNotification 
} = pcUISlice.actions;

export default pcUISlice.reducer;
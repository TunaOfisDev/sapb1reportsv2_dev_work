// frontend/src/redux/store.js
import { configureStore } from '@reduxjs/toolkit';
import salesBudgetReducer from './reducers/salesbudget/salesBudgetReducer';
import salesBudgetReducerv2 from './reducers/salesbudgetv2/salesBudgetReducerv2';

export const store = configureStore({
  reducer: {
    salesBudget: salesBudgetReducer,
    salesBudgetv2: salesBudgetReducerv2,
  },
  middleware: (getDefaultMiddleware) => getDefaultMiddleware({
    serializableCheck: false,
  })
});

export default store;
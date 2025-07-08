// frontend/src/components/ProductConfig/store/pcStore.js
import { configureStore } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import { createLogger } from 'redux-logger';
import pcConfigurationReducer from './pcConfigurationSlice';
import pcVariantReducer from './pcVariantSlice';
import pcTaxonomyReducer from './pcTaxonomySlice';
import pcUIReducer from './pcUISlice';
import pcSettingsReducer from './pcSettingsSlice';

// Persist config for the store
const persistConfig = {
  key: 'root',
  storage,
  whitelist: ['pcVariant'], // Persist only 'pcVariant'
};

// Applying persist reducer on pcVariantReducer
const persistedPcVariantReducer = persistReducer(persistConfig, pcVariantReducer);

// Root reducer combining all slices
const rootReducer = {
  pcConfiguration: pcConfigurationReducer, // Handles configuration and options
  pcVariant: persistedPcVariantReducer,    // Handles variant details
  pcTaxonomy: pcTaxonomyReducer,           // Handles taxonomy-related data
  pcUI: pcUIReducer,                       // Handles UI-related state
  pcSettings: pcSettingsReducer,
};

// Store configuration
const pcStore = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) => {
    const middleware = getDefaultMiddleware({
      serializableCheck: {
        // Allow actions with non-serializable payloads (like currentQuestion and question objects)
        ignoredActions: [
          'pcConfiguration/setCurrentQuestion',
          'persist/PERSIST',
          'persist/REHYDRATE',
        ],
        ignoredActionPaths: ['payload.question'],
        ignoredPaths: ['pcConfiguration.currentQuestion', 'pcConfiguration.options'],
      },
    });

    // Add logger middleware in development mode
    if (process.env.NODE_ENV === 'development') {
      const logger = createLogger({
        collapsed: true,
        diff: true,
      });
      middleware.push(logger);
    }

    return middleware;
  },
  devTools: process.env.NODE_ENV !== 'production',
});

// Persistor for Redux Persist
export const persistor = persistStore(pcStore);

export default pcStore;

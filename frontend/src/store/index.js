import { configureStore } from '@reduxjs/toolkit'
import authReducer from './slices/authSlice'
import merchantReducer from './slices/merchantSlice'
import discoveryReducer from './slices/discoverySlice'
import benchmarkReducer from './slices/benchmarkSlice'
import strategyReducer from './slices/strategySlice'
import campaignReducer from './slices/campaignSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    merchant: merchantReducer,
    discovery: discoveryReducer,
    benchmark: benchmarkReducer,
    strategy: strategyReducer,
    campaigns: campaignReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
})

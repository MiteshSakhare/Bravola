import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
// ✅ FIX: Import 'merchantApi' (singular), not 'merchantsAPI'
import { merchantApi } from '../../api/merchants'; 

// Async Thunks
export const fetchMerchantProfile = createAsyncThunk(
  'merchant/fetchProfile',
  async (_, { rejectWithValue }) => {
    try {
      // ✅ FIX: Use merchantApi here
      return await merchantApi.getCurrentMerchant();
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const updateMerchantIntegrations = createAsyncThunk(
  'merchant/updateIntegrations',
  async (data, { rejectWithValue }) => {
    try {
      // ✅ FIX: Use merchantApi here
      return await merchantApi.updateIntegrations(data);
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

const merchantSlice = createSlice({
  name: 'merchant',
  initialState: {
    profile: null,
    loading: false,
    error: null,
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Profile
      .addCase(fetchMerchantProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMerchantProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.profile = action.payload;
      })
      .addCase(fetchMerchantProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Update Integrations
      .addCase(updateMerchantIntegrations.pending, (state) => {
        state.loading = true;
      })
      .addCase(updateMerchantIntegrations.fulfilled, (state, action) => {
        state.loading = false;
        // Merge new data into profile
        state.profile = { ...state.profile, ...action.payload };
      })
      .addCase(updateMerchantIntegrations.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearError } = merchantSlice.actions;
export default merchantSlice.reducer;
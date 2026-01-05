import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { campaignsApi } from '../../api/campaigns';

export const fetchCampaigns = createAsyncThunk(
  'campaigns/fetchAll',
  async (_, { rejectWithValue }) => {
    try {
      return await campaignsApi.list();
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch campaigns');
    }
  }
);

const campaignSlice = createSlice({
  name: 'campaigns',
  initialState: {
    items: [],
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchCampaigns.pending, (state) => { state.loading = true; })
      .addCase(fetchCampaigns.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchCampaigns.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export default campaignSlice.reducer;
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { strategyApi } from '../../api/strategy';

export const fetchStrategies = createAsyncThunk(
  'strategy/fetchAll',
  async (filters = {}, { rejectWithValue }) => {
    try {
      return await strategyApi.list(filters.status, filters.limit);
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed');
    }
  }
);

export const generateStrategies = createAsyncThunk(
  'strategy/generate',
  async (limit, { rejectWithValue }) => {
    try {
      return await strategyApi.generate(limit);
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed');
    }
  }
);

// ✅ THIS WAS MISSING - ADD IT NOW
export const implementStrategy = createAsyncThunk(
  'strategy/implement',
  async (id, { rejectWithValue }) => {
    try {
      return await strategyApi.implement(id);
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed');
    }
  }
);

const strategySlice = createSlice({
  name: 'strategy',
  initialState: { items: [], loading: false, generating: false, error: null },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchStrategies.fulfilled, (state, action) => {
        state.items = action.payload;
        state.loading = false;
      })
      .addCase(generateStrategies.fulfilled, (state, action) => {
        state.items = [...action.payload, ...state.items];
        state.generating = false;
      })
      .addCase(implementStrategy.fulfilled, (state, action) => {
        const index = state.items.findIndex(s => s.id === action.payload.id);
        if (index !== -1) state.items[index] = action.payload;
      });
  },
});

export default strategySlice.reducer;
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { benchmarkAPI } from '@/api/benchmark'

const initialState = {
  scores: null,
  analysis: null,
  loading: false,
  error: null,
}

export const analyzeBenchmark = createAsyncThunk(
  'benchmark/analyze',
  async (forceRefresh = false, { rejectWithValue }) => {
    try {
      return await benchmarkAPI.analyze({ force_refresh: forceRefresh })
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail)
    }
  }
)

const benchmarkSlice = createSlice({
  name: 'benchmark',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(analyzeBenchmark.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(analyzeBenchmark.fulfilled, (state, action) => {
        state.loading = false
        state.analysis = action.payload
        state.scores = action.payload.benchmark
      })
      .addCase(analyzeBenchmark.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })
  },
})

export default benchmarkSlice.reducer

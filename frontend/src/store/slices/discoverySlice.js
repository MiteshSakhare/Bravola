import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { discoveryAPI } from '@/api/discovery'

const initialState = {
  profile: null,
  analysis: null,
  loading: false,
  error: null,
}

export const analyzeDiscovery = createAsyncThunk(
  'discovery/analyze',
  async (forceRefresh = false, { rejectWithValue }) => {
    try {
      return await discoveryAPI.analyze({ force_refresh: forceRefresh })
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail)
    }
  }
)

export const fetchDiscoveryProfile = createAsyncThunk(
  'discovery/fetchProfile',
  async (_, { rejectWithValue }) => {
    try {
      return await discoveryAPI.getProfile()
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail)
    }
  }
)

const discoverySlice = createSlice({
  name: 'discovery',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(analyzeDiscovery.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(analyzeDiscovery.fulfilled, (state, action) => {
        state.loading = false
        state.analysis = action.payload
        state.profile = action.payload.profile
      })
      .addCase(analyzeDiscovery.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })
      .addCase(fetchDiscoveryProfile.fulfilled, (state, action) => {
        state.profile = action.payload
      })
  },
})

export default discoverySlice.reducer

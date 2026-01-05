import apiClient from './client'

export const discoveryAPI = {
  analyze: async (params = {}) => {
    const response = await apiClient.post('/discovery/analyze', params)
    return response.data
  },

  getProfile: async () => {
    const response = await apiClient.get('/discovery/profile')
    return response.data
  },
}

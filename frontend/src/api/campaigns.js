import apiClient from './client'

export const campaignsApi = {
  // Fetch all campaigns
  list: async () => {
    const response = await apiClient.get('/campaigns')
    return response.data
  },
  
  // Get single campaign details
  get: async (id) => {
    const response = await apiClient.get(`/campaigns/${id}`)
    return response.data
  }
}
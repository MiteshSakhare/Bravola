import apiClient from './client'

// 🔴 WAS: export const merchantsAPI
// ✅ CHANGE TO:
export const merchantApi = {
  getCurrentMerchant: async () => {
    const response = await apiClient.get('/merchants/me')
    return response.data
  },

  updateMerchant: async (data) => {
    const response = await apiClient.put('/merchants/me', data)
    return response.data
  },

  getMetrics: async () => {
    const response = await apiClient.get('/merchants/me/metrics')
    return response.data
  },

  syncData: async () => {
    const response = await apiClient.post('/merchants/me/sync')
    return response.data
  },

  updateIntegrations: async (data) => {
    const response = await apiClient.put('/merchants/me/integrations', data)
    return response.data
  }
}
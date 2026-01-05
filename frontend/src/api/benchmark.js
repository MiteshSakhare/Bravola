import apiClient from './client'

export const benchmarkAPI = {
  analyze: async (params = {}) => {
    const response = await apiClient.post('/benchmark/analyze', params)
    return response.data
  },

  getScores: async (limit = 10) => {
    const response = await apiClient.get('/benchmark/scores', {
      params: { limit },
    })
    return response.data
  },
}

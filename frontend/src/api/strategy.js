import apiClient from './client'

export const strategyApi = {
  generate: async (limit = 5) => {
    const response = await apiClient.post('/strategy/generate', null, {
      params: { limit },
    })
    return response.data
  },

  list: async (status = null, limit = 20) => {
    const response = await apiClient.get('/strategy/list', {
      params: { status_filter: status, limit },
    })
    return response.data
  },

  getById: async (strategyId) => {
    const response = await apiClient.get(`/strategy/${strategyId}`)
    return response.data
  },

  update: async (strategyId, data) => {
    const response = await apiClient.put(`/strategy/${strategyId}`, data)
    return response.data
  },

  // ✅ ADDED: This matches the action in strategySlice
  implement: async (strategyId) => {
    // We use the deploy endpoint or a specific implement endpoint
    const response = await apiClient.post(`/strategy/${strategyId}/implement`)
    return response.data
  },

  deploy: async (strategyId, listId) => {
    const response = await apiClient.post(`/strategy/${strategyId}/deploy`, { 
      list_id: listId 
    })
    return response.data
  },

  recordFeedback: async (strategyId, action, comments = "") => {
    const response = await apiClient.post('/feedback/record-action', {
      strategy_id: strategyId,
      action,
      comments
    })
    return response.data
  }
}
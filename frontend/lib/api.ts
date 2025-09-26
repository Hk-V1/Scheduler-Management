import axios from 'axios'
import type { Scheduler, CreateScheduler, Log, Statistics } from './types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // You can add auth headers here if needed
    // config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail)
    } else if (error.response?.status === 500) {
      throw new Error('Server error occurred. Please try again later.')
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout. Please check your connection.')
    } else if (!error.response) {
      throw new Error('Network error. Please check your connection.')
    } else {
      throw new Error(error.message || 'An unexpected error occurred')
    }
  }
)

// Health check
export const healthCheck = async (): Promise<boolean> => {
  try {
    await api.get('/')
    return true
  } catch {
    return false
  }
}

// Scheduler endpoints
export const getSchedulers = async (): Promise<Scheduler[]> => {
  const response = await api.get<Scheduler[]>('/schedulers')
  return response.data
}

export const getScheduler = async (id: string): Promise<Scheduler> => {
  const response = await api.get<Scheduler>(`/schedulers/${id}`)
  return response.data
}

export const createScheduler = async (data: CreateScheduler): Promise<Scheduler> => {
  const response = await api.post<Scheduler>('/schedulers', data)
  return response.data
}

export const updateScheduler = async (id: string, data: Partial<CreateScheduler>): Promise<Scheduler> => {
  const response = await api.put<Scheduler>(`/schedulers/${id}`, data)
  return response.data
}

export const pauseScheduler = async (id: string): Promise<void> => {
  await api.post(`/schedulers/${id}/pause`)
}

export const resumeScheduler = async (id: string): Promise<void> => {
  await api.post(`/schedulers/${id}/resume`)
}

export const deleteScheduler = async (id: string): Promise<void> => {
  await api.delete(`/schedulers/${id}`)
}

// Log endpoints
export const getSchedulerLogs = async (id: string, limit: number = 100): Promise<Log[]> => {
  const response = await api.get<Log[]>(`/schedulers/${id}/logs`, {
    params: { limit }
  })
  return response.data
}

export const getAllLogs = async (limit: number = 100): Promise<Log[]> => {
  const response = await api.get<Log[]>('/logs', {
    params: { limit }
  })
  return response.data
}

// Statistics endpoint
export const getStatistics = async (): Promise<Statistics> => {
  const response = await api.get<Statistics>('/stats')
  return response.data
}

// Export the axios instance for custom requests if needed
export { api }
export default api

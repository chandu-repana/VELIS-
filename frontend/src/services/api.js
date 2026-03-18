import axios from 'axios'

const API_BASE = 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = 'Bearer ' + token
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    const message = error.response?.data?.detail || 'Something went wrong'
    return Promise.reject(new Error(message))
  }
)

const getUserId = () => {
  const user = localStorage.getItem('user')
  return user ? JSON.parse(user).id : 1
}

export const resumeAPI = {
  upload: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/resume/upload?user_id=' + getUserId(), formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  parse: (resumeId) => api.post('/resume/parse/' + resumeId),
  list: () => api.get('/resume/list?user_id=' + getUserId()),
  get: (resumeId) => api.get('/resume/' + resumeId),
}

export const interviewAPI = {
  create: (data) => api.post('/interview/create?user_id=' + getUserId(), data),
  start: (interviewId) => api.post('/interview/start/' + interviewId),
  getQuestions: (interviewId) => api.get('/interview/' + interviewId + '/questions'),
  getQuestion: (interviewId, index) => api.get('/interview/' + interviewId + '/question/' + index),
  list: () => api.get('/interview/list?user_id=' + getUserId()),
  get: (interviewId) => api.get('/interview/' + interviewId),
}

export const voiceAPI = {
  getTTS: (questionId) => API_BASE + '/voice/tts/' + questionId,
  submitSTT: (questionId, interviewId, audioBlob) => {
    const formData = new FormData()
    formData.append('file', audioBlob, 'response.wav')
    return api.post('/voice/stt/' + questionId + '/' + interviewId, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  getResponses: (interviewId) => api.get('/voice/interview/' + interviewId + '/responses'),
}

export const analyticsAPI = {
  evaluateInterview: (interviewId) => api.post('/analytics/evaluate-interview/' + interviewId),
  getReport: (interviewId) => api.get('/analytics/interview/' + interviewId + '/report'),
  getDashboard: () => api.get('/analytics/dashboard/' + getUserId()),
}

export default api

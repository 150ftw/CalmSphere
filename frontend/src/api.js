import axios from 'axios';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const api = axios.create({
  baseURL: API_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const register = (userData) => api.post('/auth/register', userData);
export const login = (email, password) => api.post('/auth/login', null, { params: { email, password } });

// Profile
export const completeOnboarding = (data) => api.post('/profile/onboarding', data);
export const getProfile = () => api.get('/profile');

// Chat
export const createChatSession = () => api.post('/chat/session/create');
export const getChatSessions = () => api.get('/chat/sessions');
export const getChatMessages = (sessionId) => api.get(`/chat/session/${sessionId}/messages`);
export const sendMessage = (sessionId, message) => api.post('/chat/send', { session_id: sessionId, message });

// Assessments
export const getAssessmentQuestions = (type) => api.get(`/assessment/questions/${type}`);
export const submitAssessment = (type, responses) => api.post('/assessment/submit', { assessment_type: type, responses });
export const getAssessmentHistory = (type) => api.get(`/assessment/history/${type}`);

// Mood
export const logMood = (data) => api.post('/mood/log', data);
export const getMoodHistory = () => api.get('/mood/history');

// Modules
export const getModules = () => api.get('/modules');

// Dashboard
export const getStudentDashboard = () => api.get('/dashboard/student');

// Admin
export const getAnalytics = () => api.get('/admin/analytics');
export const getAdminConfig = () => api.get('/admin/config');
export const updateAdminConfig = (data) => api.post('/admin/config', data);
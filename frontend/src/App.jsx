import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { authService } from './services/auth'
import Dashboard from './pages/Dashboard'
import ResumeUpload from './pages/ResumeUpload'
import Interview from './pages/Interview'
import Results from './pages/Results'
import Login from './pages/Login'
import Navbar from './components/shared/Navbar'

function ProtectedRoute({ children }) {
  if (!authService.isLoggedIn()) {
    return <Navigate to="/login" replace />
  }
  return children
}

function PublicRoute({ children }) {
  if (authService.isLoggedIn()) {
    return <Navigate to="/dashboard" replace />
  }
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/login" element={
          <PublicRoute><Login /></PublicRoute>
        } />
        <Route path="/*" element={
          <ProtectedRoute>
            <div className="min-h-screen bg-gray-50">
              <Navbar />
              <main className="max-w-6xl mx-auto px-4 py-8">
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/upload" element={<ResumeUpload />} />
                  <Route path="/interview/:interviewId" element={<Interview />} />
                  <Route path="/results/:interviewId" element={<Results />} />
                </Routes>
              </main>
            </div>
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  )
}

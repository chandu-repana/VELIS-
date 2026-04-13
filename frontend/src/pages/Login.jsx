import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google'
import { authService } from '../services/auth'
import toast from 'react-hot-toast'

const GOOGLE_CLIENT_ID = '176491057354-juebkc7ornc8nlhd175kn1d0fdnbh2gi.apps.googleusercontent.com'
const GITHUB_CLIENT_ID = 'Ov23li24tF4OzEewUsvS'

export default function Login() {
  const navigate = useNavigate()
  const [mode, setMode] = useState('login')
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ full_name: '', email: '', password: '' })

  const update = (k, v) => setForm(prev => ({ ...prev, [k]: v }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      if (mode === 'register') {
        await authService.register({ full_name: form.full_name, email: form.email, password: form.password })
        toast.success('Account created! Please login.')
        setMode('login')
      } else {
        await authService.login(form.email, form.password)
        toast.success('Welcome back!')
        navigate('/dashboard')
      }
    } catch (err) {
      toast.error(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/auth/google', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: credentialResponse.credential })
      })
      const data = await res.json()
      if (data.access_token) {
        localStorage.setItem('token', data.access_token)
        localStorage.setItem('user', JSON.stringify(data.user))
        toast.success('Welcome!')
        navigate('/dashboard')
      } else {
        toast.error(data.detail || 'Google login failed')
      }
    } catch (err) {
      toast.error('Google login failed')
    }
  }

  const handleGitHubLogin = () => {
    const scope = 'user:email'
    const redirectUri = encodeURIComponent('http://localhost:5173/auth/callback')
    const url = 'https://github.com/login/oauth/authorize?client_id=' + GITHUB_CLIENT_ID + '&redirect_uri=' + redirectUri + '&scope=' + scope
    window.location.href = url
  }

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <div className="w-14 h-14 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <span className="text-white font-bold text-2xl">V</span>
            </div>
            <h1 className="text-3xl font-bold text-gray-900">VELIS</h1>
            <p className="text-gray-500 mt-1">Voice Enabled AI Interview System</p>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
            <div className="flex gap-2 mb-6 bg-gray-100 rounded-lg p-1">
              {['login', 'register'].map((m) => (
                <button key={m} onClick={() => setMode(m)}
                  className={"flex-1 py-2 rounded-md text-sm font-medium transition-colors " + (mode === m ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700')}>
                  {m === 'login' ? 'Sign In' : 'Create Account'}
                </button>
              ))}
            </div>

            <div className="space-y-3 mb-6">
              <div className="w-full flex justify-center">
                <GoogleLogin
                  onSuccess={handleGoogleSuccess}
                  onError={() => toast.error('Google login failed')}
                  width="368"
                  text={mode === 'login' ? 'signin_with' : 'signup_with'}
                  shape="rectangular"
                  theme="outline"
                />
              </div>

              <button onClick={handleGitHubLogin}
                className="w-full flex items-center justify-center gap-3 bg-gray-900 text-white rounded-lg px-4 py-2.5 hover:bg-gray-800 transition-colors text-sm font-medium">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
                  <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
                </svg>
                Continue with GitHub
              </button>
            </div>

            <div className="flex items-center gap-3 mb-6">
              <div className="flex-1 h-px bg-gray-200" />
              <span className="text-xs text-gray-400">or use email</span>
              <div className="flex-1 h-px bg-gray-200" />
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              {mode === 'register' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                  <input type="text" required value={form.full_name} onChange={(e) => update('full_name', e.target.value)}
                    placeholder="John Doe"
                    className="w-full border border-gray-200 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm" />
                </div>
              )}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input type="email" required value={form.email} onChange={(e) => update('email', e.target.value)}
                  placeholder="you@example.com"
                  className="w-full border border-gray-200 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                <input type="password" required value={form.password} onChange={(e) => update('password', e.target.value)}
                  placeholder="Enter your password"
                  className="w-full border border-gray-200 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm" />
              </div>
              <button type="submit" disabled={loading}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors mt-2">
                {loading ? 'Please wait...' : mode === 'login' ? 'Sign In' : 'Create Account'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </GoogleOAuthProvider>
  )
}

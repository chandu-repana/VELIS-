import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

export default function GitHubCallback() {
  const navigate = useNavigate()
  const called = useRef(false)

  useEffect(() => {
    if (called.current) return
    called.current = true

    const params = new URLSearchParams(window.location.search)
    const code = params.get('code')
    const error = params.get('error')

    if (error) {
      toast.error('GitHub login cancelled')
      navigate('/login')
      return
    }

    if (!code) {
      toast.error('No code received from GitHub')
      navigate('/login')
      return
    }

    fetch('http://localhost:8000/api/v1/auth/github', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code })
    })
      .then(async res => {
        const data = await res.json()
        if (res.ok && data.access_token) {
          localStorage.setItem('token', data.access_token)
          localStorage.setItem('user', JSON.stringify(data.user))
          toast.success('Welcome ' + data.user.full_name + '!')
          navigate('/dashboard')
        } else {
          toast.error(data.detail || 'GitHub login failed')
          navigate('/login')
        }
      })
      .catch(() => {
        toast.error('GitHub login failed')
        navigate('/login')
      })
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-800 mx-auto mb-4"></div>
        <p className="text-gray-600 font-medium">Signing in with GitHub...</p>
        <p className="text-gray-400 text-sm mt-2">Please wait...</p>
      </div>
    </div>
  )
}

import { Link, useLocation, useNavigate } from 'react-router-dom'
import { authService } from '../../services/auth'
import toast from 'react-hot-toast'

export default function Navbar() {
  const location = useLocation()
  const navigate = useNavigate()
  const user = authService.getUser()

  const links = [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/upload', label: 'New Interview' },
  ]

  const handleLogout = () => {
    authService.logout()
    toast.success('Logged out')
    navigate('/login')
  }

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">V</span>
            </div>
            <span className="font-bold text-xl text-gray-900">VELIS</span>
          </Link>
          <div className="flex items-center gap-6">
            {links.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={"text-sm font-medium transition-colors " + (
                  location.pathname === link.to
                    ? 'text-blue-600 border-b-2 border-blue-600 pb-1'
                    : 'text-gray-600 hover:text-blue-600'
                )}
              >
                {link.label}
              </Link>
            ))}
            {user && (
              <div className="flex items-center gap-3">
                <span className="text-sm text-gray-600">{user.full_name}</span>
                <button
                  onClick={handleLogout}
                  className="text-sm text-red-500 hover:text-red-600 font-medium"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

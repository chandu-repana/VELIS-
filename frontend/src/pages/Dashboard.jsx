import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { analyticsAPI, interviewAPI } from '../services/api'
import toast from 'react-hot-toast'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(null)
  const [confirmDelete, setConfirmDelete] = useState(null)

  const fetchData = () => {
    analyticsAPI.getDashboard(1)
      .then(res => setData(res.data))
      .catch(() => toast.error('Failed to load dashboard'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchData() }, [])

  const handleDelete = async (interviewId) => {
    setDeleting(interviewId)
    try {
      await interviewAPI.delete(interviewId)
      toast.success('Interview deleted')
      setConfirmDelete(null)
      fetchData()
    } catch (err) {
      toast.error('Failed to delete interview')
    } finally {
      setDeleting(null)
    }
  }

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
  )

  return (
    <div className="space-y-8">
      {confirmDelete && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-sm w-full mx-4 shadow-2xl">
            <h3 className="text-lg font-bold text-gray-900 mb-2">Delete Interview?</h3>
            <p className="text-gray-500 text-sm mb-6">This will permanently delete the interview and all responses. This cannot be undone.</p>
            <div className="flex gap-3">
              <button
                onClick={() => setConfirmDelete(null)}
                className="flex-1 border border-gray-200 text-gray-700 py-2.5 rounded-lg font-medium hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(confirmDelete)}
                disabled={deleting === confirmDelete}
                className="flex-1 bg-red-500 text-white py-2.5 rounded-lg font-medium hover:bg-red-600 disabled:opacity-50 transition-colors"
              >
                {deleting === confirmDelete ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 mt-1">Track your interview performance</p>
        </div>
        <Link to="/upload" className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors">
          Start New Interview
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[
          { label: 'Total Interviews', value: data?.total_interviews ?? 0, color: 'text-blue-700' },
          { label: 'Completed', value: data?.completed_interviews ?? 0, color: 'text-green-700' },
          { label: 'Average Score', value: data?.average_score ? data.average_score + '/10' : 'N/A', color: 'text-purple-700' },
          { label: 'Best Score', value: data?.best_score ? data.best_score + '/10' : 'N/A', color: 'text-orange-700' },
        ].map((stat) => (
          <div key={stat.label} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <p className="text-sm text-gray-500">{stat.label}</p>
            <p className={"text-3xl font-bold mt-2 " + stat.color}>{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-6 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">Recent Interviews</h2>
        </div>
        {!data?.interviews?.length ? (
          <div className="p-12 text-center">
            <p className="text-gray-400 text-lg">No interviews yet</p>
            <Link to="/upload" className="mt-4 inline-block text-blue-600 hover:underline">
              Start your first interview
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {data.interviews.map((interview) => (
              <div key={interview.id} className="p-6 flex items-center justify-between hover:bg-gray-50 transition-colors">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{interview.title}</p>
                  <p className="text-sm text-gray-500 mt-1">{interview.job_role} - {new Date(interview.created_at).toLocaleDateString()}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={"px-3 py-1 rounded-full text-xs font-medium " + (
                    interview.status === 'completed' ? 'bg-green-100 text-green-700' :
                    interview.status === 'in_progress' ? 'bg-blue-100 text-blue-700' :
                    'bg-gray-100 text-gray-600'
                  )}>
                    {interview.status.replace('_', ' ')}
                  </span>
                  {interview.overall_score && (
                    <span className="font-bold text-gray-900">{interview.overall_score}/10</span>
                  )}
                  {interview.status === 'in_progress' && (
                    <Link
                      to={"/interview/" + interview.id}
                      className="px-3 py-1.5 bg-blue-600 text-white rounded-lg text-xs font-medium hover:bg-blue-700 transition-colors"
                    >
                      Resume
                    </Link>
                  )}
                  <Link
                    to={"/results/" + interview.id}
                    className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    View
                  </Link>
                  <button
                    onClick={() => setConfirmDelete(interview.id)}
                    className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete interview"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

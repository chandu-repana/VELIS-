import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { analyticsAPI } from '../services/api'
import toast from 'react-hot-toast'

const GRADE_COLORS = {
  'A+': 'text-emerald-600', 'A': 'text-green-600',
  'B': 'text-blue-600', 'C+': 'text-yellow-600',
  'C': 'text-yellow-500', 'D': 'text-orange-600',
  'F': 'text-red-600', 'N/A': 'text-gray-400'
}

const TYPE_LABELS = {
  technical: '⚙️ Technical', behavioral: '🧠 Behavioral',
  situational: '💡 Situational', general: '💬 General'
}

export default function Results() {
  const { interviewId } = useParams()
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    analyticsAPI.getReport(interviewId)
      .then(res => setReport(res.data))
      .catch(() => toast.error('Failed to load report'))
      .finally(() => setLoading(false))
  }, [interviewId])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-500">Loading your results...</p>
      </div>
    </div>
  )

  if (!report) return (
    <div className="text-center py-16">
      <p className="text-gray-500 text-lg">Report not available</p>
      <Link to="/dashboard" className="text-blue-600 hover:underline mt-2 inline-block">Back to Dashboard</Link>
    </div>
  )

  const grade = report.overall_feedback?.grade || 'N/A'
  const score = report.overall_score || 0
  const gradeColor = GRADE_COLORS[grade] || 'text-gray-600'
  const scoreColor = score >= 7 ? 'bg-green-500' : score >= 5 ? 'bg-yellow-500' : 'bg-red-500'
  const categoryScores = report.overall_feedback?.category_scores || {}

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Interview Results</h1>
          <p className="text-gray-500 mt-1">{report.job_role}</p>
        </div>
        <Link to="/dashboard" className="text-blue-600 hover:text-blue-700 font-medium text-sm">
          Back to Dashboard
        </Link>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
        <div className="flex items-start justify-between mb-6 flex-wrap gap-4">
          <div>
            <p className="text-sm text-gray-500 mb-2">Overall Score</p>
            <div className="flex items-end gap-3">
              <span className="text-6xl font-bold text-gray-900">{score}</span>
              <span className="text-2xl text-gray-400 mb-2">/10</span>
              <span className={"text-5xl font-bold mb-1 " + gradeColor}>{grade}</span>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500 mb-1">Questions Answered</p>
            <p className="text-3xl font-bold text-gray-900">{report.answered_questions}/{report.total_questions}</p>
            <p className="text-xs text-gray-400 mt-1">{report.status.replace('_', ' ')}</p>
          </div>
        </div>

        <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
          <div className={"h-3 rounded-full transition-all " + scoreColor} style={{ width: (score / 10 * 100) + '%' }} />
        </div>

        <p className="text-gray-700 text-sm leading-relaxed">{report.overall_feedback?.summary}</p>
      </div>

      {Object.keys(categoryScores).length > 0 && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Performance by Category</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(categoryScores).map(([type, catScore]) => (
              <div key={type} className="text-center p-4 bg-gray-50 rounded-xl">
                <p className="text-xs text-gray-500 mb-1">{TYPE_LABELS[type] || type}</p>
                <p className={"text-2xl font-bold " + (catScore >= 7 ? 'text-green-600' : catScore >= 5 ? 'text-yellow-600' : 'text-red-600')}>
                  {catScore}
                </p>
                <p className="text-xs text-gray-400">/10</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        {report.overall_feedback?.top_strengths?.length > 0 && (
          <div className="bg-green-50 border border-green-200 rounded-2xl p-6">
            <h3 className="font-semibold text-green-800 mb-3">✅ Top Strengths</h3>
            <ul className="space-y-2">
              {report.overall_feedback.top_strengths.map((s, i) => (
                <li key={i} className="text-green-700 text-sm flex items-start gap-2">
                  <span className="mt-0.5 flex-shrink-0">•</span><span>{s}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        {report.overall_feedback?.top_improvements?.length > 0 && (
          <div className="bg-orange-50 border border-orange-200 rounded-2xl p-6">
            <h3 className="font-semibold text-orange-800 mb-3">🎯 Key Improvements</h3>
            <ul className="space-y-2">
              {report.overall_feedback.top_improvements.map((s, i) => (
                <li key={i} className="text-orange-700 text-sm flex items-start gap-2">
                  <span className="mt-0.5 flex-shrink-0">→</span><span>{s}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100">
        <div className="flex border-b border-gray-100">
          {['overview', 'detailed'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={"flex-1 py-3 text-sm font-medium transition-colors " + (
                activeTab === tab
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              )}
            >
              {tab === 'overview' ? 'Score Overview' : 'Question by Question'}
            </button>
          ))}
        </div>

        {activeTab === 'overview' && (
          <div className="p-6 space-y-3">
            {report.detailed_results?.map((item, idx) => (
              <div key={idx} className="flex items-center gap-4 p-3 rounded-xl hover:bg-gray-50">
                <span className="text-sm font-medium text-gray-500 w-6 flex-shrink-0">Q{idx + 1}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-800 truncate">{item.question}</p>
                  <span className={"text-xs px-2 py-0.5 rounded-full " + (
                    item.question_type === 'technical' ? 'bg-blue-100 text-blue-600' :
                    item.question_type === 'behavioral' ? 'bg-purple-100 text-purple-600' :
                    item.question_type === 'situational' ? 'bg-yellow-100 text-yellow-600' :
                    'bg-gray-100 text-gray-600'
                  )}>{item.question_type}</span>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div
                      className={"h-2 rounded-full " + (item.score >= 7 ? 'bg-green-500' : item.score >= 5 ? 'bg-yellow-500' : 'bg-red-500')}
                      style={{ width: (item.score / 10 * 100) + '%' }}
                    />
                  </div>
                  <span className="text-sm font-bold text-gray-900 w-8">{item.score}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'detailed' && (
          <div className="divide-y divide-gray-50">
            {report.detailed_results?.map((item, idx) => (
              <div key={idx} className="p-6 space-y-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                      <span className="text-xs font-bold text-gray-400">Q{idx + 1}</span>
                      <span className={"text-xs px-2 py-0.5 rounded-full font-medium " + (
                        item.question_type === 'technical' ? 'bg-blue-100 text-blue-700' :
                        item.question_type === 'behavioral' ? 'bg-purple-100 text-purple-700' :
                        item.question_type === 'situational' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-gray-100 text-gray-600'
                      )}>{TYPE_LABELS[item.question_type] || item.question_type}</span>
                      {item.skill_tag && (
                        <span className="text-xs px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded-full font-medium">
                          {item.skill_tag}
                        </span>
                      )}
                    </div>
                    <p className="font-medium text-gray-900">{item.question}</p>
                  </div>
                  <div className="flex-shrink-0 text-center">
                    <span className={"text-3xl font-bold " + (item.score >= 7 ? 'text-green-600' : item.score >= 5 ? 'text-yellow-600' : 'text-red-600')}>
                      {item.score}
                    </span>
                    <span className="text-gray-400 text-sm">/10</span>
                  </div>
                </div>

                {item.answer && (
                  <div className="bg-gray-50 rounded-xl p-4">
                    <p className="text-xs font-medium text-gray-500 mb-1">Your Answer</p>
                    <p className="text-sm text-gray-700 italic">"{item.answer}"</p>
                  </div>
                )}

                <p className="text-sm text-gray-600 bg-blue-50 rounded-lg p-3">{item.feedback}</p>

                <div className="grid grid-cols-2 gap-4">
                  {item.strengths?.length > 0 && (
                    <div className="bg-green-50 rounded-xl p-4">
                      <p className="text-xs font-semibold text-green-700 mb-2">✅ Strengths</p>
                      {item.strengths.map((s, i) => (
                        <p key={i} className="text-xs text-gray-700 mb-1">• {s}</p>
                      ))}
                    </div>
                  )}
                  {item.improvements?.length > 0 && (
                    <div className="bg-orange-50 rounded-xl p-4">
                      <p className="text-xs font-semibold text-orange-700 mb-2">🎯 Improvements</p>
                      {item.improvements.map((s, i) => (
                        <p key={i} className="text-xs text-gray-700 mb-1">• {s}</p>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="flex gap-4">
        <Link to="/upload" className="flex-1 text-center bg-blue-600 text-white py-3 rounded-xl font-medium hover:bg-blue-700 transition-colors">
          Start New Interview
        </Link>
        <Link to="/dashboard" className="flex-1 text-center border border-gray-200 text-gray-700 py-3 rounded-xl font-medium hover:bg-gray-50 transition-colors">
          View Dashboard
        </Link>
      </div>
    </div>
  )
}

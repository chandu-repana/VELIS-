import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { analyticsAPI } from '../services/api'
import toast from 'react-hot-toast'

export default function Results() {
  const { interviewId } = useParams()
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    analyticsAPI.getReport(interviewId)
      .then(res => setReport(res.data))
      .catch(() => toast.error('Failed to load report'))
      .finally(() => setLoading(false))
  }, [interviewId])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
  )

  if (!report) return (
    <div className="text-center py-16">
      <p className="text-gray-500">Report not available</p>
      <Link to="/dashboard" className="text-blue-600 hover:underline mt-2 inline-block">Back to Dashboard</Link>
    </div>
  )

  const grade = report.overall_feedback?.grade || 'N/A'
  const score = report.overall_score || 0
  const gradeColor = grade === 'A' ? 'text-green-600' : grade === 'B' ? 'text-blue-600' : grade === 'C' ? 'text-yellow-600' : 'text-red-600'

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Interview Results</h1>
          <p className="text-gray-500 mt-1">{report.job_role}</p>
        </div>
        <Link to="/dashboard" className="text-blue-600 hover:text-blue-700 font-medium">Back to Dashboard</Link>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="text-sm text-gray-500 mb-1">Overall Score</p>
            <div className="flex items-end gap-3">
              <span className="text-5xl font-bold text-gray-900">{score}</span>
              <span className="text-2xl text-gray-400 mb-1">/10</span>
              <span className={"text-4xl font-bold mb-1 " + gradeColor}>{grade}</span>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Questions Answered</p>
            <p className="text-2xl font-bold text-gray-900">{report.answered_questions}/{report.total_questions}</p>
          </div>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 mb-6">
          <div className={"h-3 rounded-full transition-all " + (score >= 7 ? 'bg-green-500' : score >= 5 ? 'bg-yellow-500' : 'bg-red-500')} style={{ width: (score / 10 * 100) + '%' }} />
        </div>
        <p className="text-gray-700">{report.overall_feedback?.summary}</p>
      </div>

      {report.overall_feedback?.top_strengths?.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-6">
          <h3 className="font-semibold text-green-800 mb-3">Top Strengths</h3>
          <ul className="space-y-2">
            {report.overall_feedback.top_strengths.map((s, i) => (
              <li key={i} className="flex items-start gap-2 text-green-700 text-sm"><span>✓</span><span>{s}</span></li>
            ))}
          </ul>
        </div>
      )}

      {report.overall_feedback?.top_improvements?.length > 0 && (
        <div className="bg-orange-50 border border-orange-200 rounded-xl p-6">
          <h3 className="font-semibold text-orange-800 mb-3">Areas for Improvement</h3>
          <ul className="space-y-2">
            {report.overall_feedback.top_improvements.map((s, i) => (
              <li key={i} className="flex items-start gap-2 text-orange-700 text-sm"><span>→</span><span>{s}</span></li>
            ))}
          </ul>
        </div>
      )}

      {report.detailed_results?.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">Question by Question</h2>
          {report.detailed_results.map((item, idx) => (
            <div key={idx} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div className="flex items-start justify-between gap-4 mb-4">
                <p className="font-medium text-gray-900 flex-1">{item.question}</p>
                <div className="flex items-center gap-1 flex-shrink-0">
                  <span className="text-2xl font-bold text-gray-900">{item.score}</span>
                  <span className="text-gray-400">/10</span>
                </div>
              </div>
              {item.answer && (
                <div className="bg-gray-50 rounded-lg p-3 mb-3">
                  <p className="text-xs text-gray-500 mb-1">Your answer</p>
                  <p className="text-sm text-gray-700">{item.answer}</p>
                </div>
              )}
              <p className="text-sm text-gray-600 mb-3">{item.feedback}</p>
              <div className="grid grid-cols-2 gap-4">
                {item.strengths?.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-green-700 mb-1">Strengths</p>
                    {item.strengths.map((s, i) => <p key={i} className="text-xs text-gray-600">- {s}</p>)}
                  </div>
                )}
                {item.improvements?.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-orange-700 mb-1">Improvements</p>
                    {item.improvements.map((s, i) => <p key={i} className="text-xs text-gray-600">- {s}</p>)}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="flex gap-4 pb-8">
        <Link to="/upload" className="flex-1 text-center bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors">Start New Interview</Link>
        <Link to="/dashboard" className="flex-1 text-center border border-gray-200 text-gray-700 py-3 rounded-lg font-medium hover:bg-gray-50 transition-colors">View Dashboard</Link>
      </div>
    </div>
  )
}

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { resumeAPI, interviewAPI } from '../services/api'
import toast from 'react-hot-toast'

export default function ResumeUpload() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [file, setFile] = useState(null)
  const [resume, setResume] = useState(null)
  const [jobRole, setJobRole] = useState('Software Developer')
  const [numQuestions, setNumQuestions] = useState(10)
  const [loading, setLoading] = useState(false)
  const [dragOver, setDragOver] = useState(false)

  const handleFile = (f) => {
    if (!f) return
    const allowed = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!allowed.includes(f.type)) {
      toast.error('Only PDF and DOCX files are allowed')
      return
    }
    setFile(f)
  }

  const handleUpload = async () => {
    if (!file) return toast.error('Please select a file')
    setLoading(true)
    try {
      const uploadRes = await resumeAPI.upload(file, 1)
      const resumeId = uploadRes.data.id
      toast.success('Resume uploaded!')
      const parseRes = await resumeAPI.parse(resumeId)
      setResume(parseRes.data)
      toast.success('Extracted ' + parseRes.data.extracted_skills.length + ' skills!')
      setStep(2)
    } catch (err) {
      toast.error(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleStartInterview = async () => {
    setLoading(true)
    try {
      const res = await interviewAPI.create({
        resume_id: resume.id,
        job_role: jobRole,
        num_questions: numQuestions,
        title: jobRole + ' Interview'
      })
      const interviewId = res.data.interview_id
      await interviewAPI.start(interviewId)
      toast.success('Interview created!')
      navigate('/interview/' + interviewId)
    } catch (err) {
      toast.error(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">New Interview</h1>
        <p className="text-gray-500 mt-1">Upload your resume to get started</p>
      </div>

      <div className="flex items-center gap-4 mb-8">
        {[1, 2].map((s) => (
          <div key={s} className="flex items-center gap-2">
            <div className={"w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold " + (step >= s ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500')}>
              {s}
            </div>
            <span className={"text-sm " + (step >= s ? 'text-blue-600 font-medium' : 'text-gray-400')}>
              {s === 1 ? 'Upload Resume' : 'Configure Interview'}
            </span>
            {s < 2 && <div className={"w-16 h-0.5 " + (step > s ? 'bg-blue-600' : 'bg-gray-200')} />}
          </div>
        ))}
      </div>

      {step === 1 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 space-y-6">
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]) }}
            className={"border-2 border-dashed rounded-xl p-12 text-center transition-colors cursor-pointer " + (dragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-400')}
            onClick={() => document.getElementById('fileInput').click()}
          >
            <div className="text-5xl mb-4">📄</div>
            {file ? (
              <div>
                <p className="font-medium text-gray-900">{file.name}</p>
                <p className="text-sm text-gray-500 mt-1">{(file.size / 1024).toFixed(0)} KB</p>
              </div>
            ) : (
              <div>
                <p className="font-medium text-gray-700">Drop your resume here</p>
                <p className="text-sm text-gray-400 mt-1">PDF or DOCX, up to 10MB</p>
              </div>
            )}
            <input id="fileInput" type="file" accept=".pdf,.docx" className="hidden" onChange={(e) => handleFile(e.target.files[0])} />
          </div>
          <button onClick={handleUpload} disabled={!file || loading} className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
            {loading ? 'Processing...' : 'Upload and Extract Skills'}
          </button>
        </div>
      )}

      {step === 2 && resume && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 space-y-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="font-medium text-green-800">Resume parsed successfully</p>
            <p className="text-sm text-green-600 mt-1">{resume.extracted_skills.length} skills extracted</p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-700 mb-2">Extracted Skills</p>
            <div className="flex flex-wrap gap-2">
              {resume.extracted_skills.length > 0 ? resume.extracted_skills.map((skill) => (
                <span key={skill} className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-medium">{skill}</span>
              )) : <p className="text-gray-400 text-sm">No skills detected</p>}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Job Role</label>
              <input value={jobRole} onChange={(e) => setJobRole(e.target.value)} className="w-full border border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Number of Questions</label>
              <select value={numQuestions} onChange={(e) => setNumQuestions(Number(e.target.value))} className="w-full border border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
                {[5, 8, 10, 15].map(n => <option key={n} value={n}>{n} questions</option>)}
              </select>
            </div>
          </div>
          <button onClick={handleStartInterview} disabled={loading} className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors">
            {loading ? 'Creating Interview...' : 'Start Interview'}
          </button>
        </div>
      )}
    </div>
  )
}

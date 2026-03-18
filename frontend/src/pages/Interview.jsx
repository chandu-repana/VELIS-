import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { interviewAPI, voiceAPI, analyticsAPI } from '../services/api'
import toast from 'react-hot-toast'

export default function Interview() {
  const { interviewId } = useParams()
  const navigate = useNavigate()
  const [questions, setQuestions] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [recording, setRecording] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [answered, setAnswered] = useState({})
  const [audioPlaying, setAudioPlaying] = useState(false)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const audioRef = useRef(null)

  useEffect(() => {
    interviewAPI.getQuestions(interviewId)
      .then(res => setQuestions(res.data))
      .catch(() => toast.error('Failed to load questions'))
  }, [interviewId])

  const currentQuestion = questions[currentIndex]
  const progress = questions.length > 0 ? ((currentIndex / questions.length) * 100) : 0

  const playQuestion = () => {
    if (!currentQuestion) return
    const url = voiceAPI.getTTS(currentQuestion.id)
    if (audioRef.current) {
      audioRef.current.src = url
      audioRef.current.play()
      setAudioPlaying(true)
      audioRef.current.onended = () => setAudioPlaying(false)
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      audioChunksRef.current = []
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      mediaRecorder.ondataavailable = (e) => audioChunksRef.current.push(e.data)
      mediaRecorder.start()
      setRecording(true)
      toast.success('Recording started')
    } catch (err) {
      toast.error('Microphone access denied')
    }
  }

  const stopRecording = async () => {
    if (!mediaRecorderRef.current) return
    setRecording(false)
    setProcessing(true)
    mediaRecorderRef.current.stop()
    mediaRecorderRef.current.stream.getTracks().forEach(t => t.stop())
    mediaRecorderRef.current.onstop = async () => {
      try {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        const res = await voiceAPI.submitSTT(currentQuestion.id, interviewId, audioBlob)
        setAnswered(prev => ({ ...prev, [currentIndex]: res.data }))
        toast.success('Answer recorded!')
      } catch (err) {
        toast.error('Transcription failed: ' + err.message)
      } finally {
        setProcessing(false)
      }
    }
  }

  const nextQuestion = () => {
    if (currentIndex < questions.length - 1) setCurrentIndex(prev => prev + 1)
  }

  const finishInterview = async () => {
    setProcessing(true)
    try {
      await analyticsAPI.evaluateInterview(interviewId)
      toast.success('Interview complete!')
      navigate('/results/' + interviewId)
    } catch (err) {
      toast.error('Failed to finalize interview')
    } finally {
      setProcessing(false)
    }
  }

  if (questions.length === 0) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
  )

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <audio ref={audioRef} className="hidden" />
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Interview Session</h1>
        <span className="text-sm text-gray-500">Question {currentIndex + 1} of {questions.length}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div className="bg-blue-600 h-2 rounded-full transition-all duration-500" style={{ width: progress + '%' }} />
      </div>

      {currentQuestion && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 space-y-6">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-blue-600 font-bold">{currentIndex + 1}</span>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3">
                <span className={"px-2 py-0.5 rounded text-xs font-medium " + (currentQuestion.difficulty === 'easy' ? 'bg-green-100 text-green-700' : currentQuestion.difficulty === 'hard' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700')}>
                  {currentQuestion.difficulty}
                </span>
                <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs font-medium">{currentQuestion.question_type}</span>
                {currentQuestion.skill_tag && (
                  <span className="px-2 py-0.5 bg-blue-100 text-blue-600 rounded text-xs font-medium">{currentQuestion.skill_tag}</span>
                )}
              </div>
              <p className="text-lg text-gray-900 leading-relaxed">{currentQuestion.text}</p>
            </div>
          </div>

          <button onClick={playQuestion} disabled={audioPlaying} className="flex items-center gap-2 px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 disabled:opacity-50 transition-colors text-sm font-medium">
            {audioPlaying ? '🔊 Playing...' : '🔊 Listen to Question'}
          </button>

          <div className="border-t border-gray-100 pt-6">
            <p className="text-sm font-medium text-gray-700 mb-4">Your Answer</p>
            {!answered[currentIndex] ? (
              <div className="space-y-4">
                <div className={"flex items-center gap-3 p-4 rounded-xl border-2 " + (recording ? 'border-red-400 bg-red-50' : 'border-gray-200 bg-gray-50')}>
                  <div className={"w-4 h-4 rounded-full " + (recording ? 'bg-red-500 animate-pulse' : 'bg-gray-300')} />
                  <span className="text-sm text-gray-600">
                    {recording ? 'Recording in progress...' : processing ? 'Processing your answer...' : 'Ready to record'}
                  </span>
                </div>
                {!recording ? (
                  <button onClick={startRecording} disabled={processing} className="w-full bg-red-500 text-white py-3 rounded-lg font-medium hover:bg-red-600 disabled:opacity-50 transition-colors">
                    🎤 Start Recording
                  </button>
                ) : (
                  <button onClick={stopRecording} className="w-full bg-gray-800 text-white py-3 rounded-lg font-medium hover:bg-gray-900 transition-colors">
                    Stop Recording
                  </button>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-sm font-medium text-green-800 mb-1">Answer recorded</p>
                  <p className="text-sm text-gray-700">{answered[currentIndex].transcribed_text || 'No transcription available'}</p>
                </div>
                {currentIndex < questions.length - 1 ? (
                  <button onClick={nextQuestion} className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors">
                    Next Question
                  </button>
                ) : (
                  <button onClick={finishInterview} disabled={processing} className="w-full bg-green-600 text-white py-3 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 transition-colors">
                    {processing ? 'Generating Report...' : 'Finish and Get Results'}
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      <div className="grid grid-cols-10 gap-2">
        {questions.map((_, idx) => (
          <div key={idx} className={"h-2 rounded-full " + (idx < currentIndex ? 'bg-green-400' : idx === currentIndex ? 'bg-blue-600' : 'bg-gray-200')} />
        ))}
      </div>
    </div>
  )
}

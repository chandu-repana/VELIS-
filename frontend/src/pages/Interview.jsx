import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { interviewAPI, voiceAPI, analyticsAPI } from '../services/api'
import toast from 'react-hot-toast'

const MIN_RECORDING_MS = 2000
const MAX_RECORDING_MS = 90000
const MIN_AUDIO_BYTES = 5000

export default function Interview() {
  const { interviewId } = useParams()
  const navigate = useNavigate()
  const [questions, setQuestions] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [recording, setRecording] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [answered, setAnswered] = useState({})
  const [audioPlaying, setAudioPlaying] = useState(false)
  const [audioError, setAudioError] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [loadingInterview, setLoadingInterview] = useState(true)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const audioRef = useRef(null)
  const recordingStartRef = useRef(null)
  const timerRef = useRef(null)

  useEffect(() => {
    const loadInterview = async () => {
      try {
        const [questionsRes, responsesRes] = await Promise.all([
          interviewAPI.getQuestions(interviewId),
          voiceAPI.getResponses(interviewId)
        ])
        const qs = questionsRes.data
        setQuestions(qs)
        const existingResponses = responsesRes.data || []
        const answeredMap = {}
        let lastAnsweredIndex = -1
        existingResponses.forEach(response => {
          const question = qs.find(q => q.id === response.question_id)
          if (question && response.transcribed_text) {
            answeredMap[question.order_index] = {
              transcribed_text: response.transcribed_text,
              response_id: response.id
            }
            if (question.order_index > lastAnsweredIndex) {
              lastAnsweredIndex = question.order_index
            }
          }
        })
        setAnswered(answeredMap)
        if (lastAnsweredIndex >= 0 && lastAnsweredIndex < qs.length - 1) {
          setCurrentIndex(lastAnsweredIndex + 1)
          toast.success('Resuming from question ' + (lastAnsweredIndex + 2))
        } else if (lastAnsweredIndex === qs.length - 1) {
          setCurrentIndex(qs.length - 1)
        }
      } catch (err) {
        toast.error('Failed to load interview')
      } finally {
        setLoadingInterview(false)
      }
    }
    loadInterview()
  }, [interviewId])

  useEffect(() => {
    return () => { if (timerRef.current) clearInterval(timerRef.current) }
  }, [])

  const currentQuestion = questions[currentIndex]
  const progress = questions.length > 0 ? (Object.keys(answered).length / questions.length) * 100 : 0
  const answeredCount = Object.keys(answered).length

  const playQuestion = async () => {
    if (!currentQuestion) return
    setAudioError(false)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(
        'http://localhost:8000/api/v1/voice/tts/' + currentQuestion.id,
        { method: 'POST', headers: { Authorization: 'Bearer ' + token } }
      )
      if (!response.ok) throw new Error('TTS failed')
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      if (audioRef.current) {
        audioRef.current.src = url
        audioRef.current.load()
        setAudioPlaying(true)
        await audioRef.current.play()
        audioRef.current.onended = () => { setAudioPlaying(false); URL.revokeObjectURL(url) }
      }
    } catch (err) {
      setAudioError(true)
      setAudioPlaying(false)
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true, sampleRate: 16000 }
      })
      audioChunksRef.current = []
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      mediaRecorderRef.current = mediaRecorder
      mediaRecorder.ondataavailable = (e) => { if (e.data.size > 0) audioChunksRef.current.push(e.data) }
      mediaRecorder.start(200)
      recordingStartRef.current = Date.now()
      setRecording(true)
      setRecordingTime(0)
      timerRef.current = setInterval(() => {
        setRecordingTime(Math.floor((Date.now() - recordingStartRef.current) / 1000))
      }, 1000)
      toast.success('Recording started — speak your answer clearly')
    } catch (err) {
      toast.error('Microphone access denied. Please allow microphone in browser settings.')
    }
  }

  const stopRecording = async () => {
    if (!mediaRecorderRef.current) return
    const duration = Date.now() - (recordingStartRef.current || Date.now())
    if (timerRef.current) clearInterval(timerRef.current)

    if (duration < MIN_RECORDING_MS) {
      toast.error('Recording too short — please speak for at least 2 seconds')
      mediaRecorderRef.current.stop()
      mediaRecorderRef.current.stream.getTracks().forEach(t => t.stop())
      setRecording(false)
      setRecordingTime(0)
      return
    }

    setRecording(false)
    setProcessing(true)
    mediaRecorderRef.current.stop()
    mediaRecorderRef.current.stream.getTracks().forEach(t => t.stop())

    mediaRecorderRef.current.onstop = async () => {
      try {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        if (audioBlob.size < MIN_AUDIO_BYTES) {
          toast.error('No audio detected — check your microphone and try again')
          setProcessing(false)
          return
        }
        const res = await voiceAPI.submitSTT(currentQuestion.id, interviewId, audioBlob)
        const transcribed = res.data.transcribed_text
        if (!transcribed || transcribed.trim().length < 5) {
          toast.error('Could not understand your speech. Speak louder and more clearly, then try again.')
          setProcessing(false)
          return
        }
        setAnswered(prev => ({ ...prev, [currentIndex]: res.data }))
        toast.success('Answer recorded successfully!')
      } catch (err) {
        toast.error('Recording failed: ' + err.message)
      } finally {
        setProcessing(false)
        setRecordingTime(0)
      }
    }
  }

  const nextQuestion = () => {
    if (currentIndex < questions.length - 1) setCurrentIndex(prev => prev + 1)
  }

  const prevQuestion = () => {
    if (currentIndex > 0) setCurrentIndex(prev => prev - 1)
  }

  const finishInterview = async () => {
    const unanswered = questions.length - answeredCount
    if (unanswered > 0) {
      const confirmed = window.confirm(unanswered + ' questions are unanswered. Finish anyway?')
      if (!confirmed) return
    }
    setProcessing(true)
    try {
      await analyticsAPI.evaluateInterview(interviewId)
      toast.success('Interview complete! Generating your report...')
      navigate('/results/' + interviewId)
    } catch (err) {
      toast.error('Failed to finalize: ' + err.message)
    } finally {
      setProcessing(false)
    }
  }

  if (loadingInterview) return (
    <div className="flex items-center justify-center h-64">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-500">Loading your interview...</p>
      </div>
    </div>
  )

  if (questions.length === 0) return (
    <div className="text-center py-16">
      <p className="text-gray-500">No questions found for this interview.</p>
    </div>
  )

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <audio ref={audioRef} className="hidden" />

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Interview Session</h1>
          <p className="text-sm text-gray-500 mt-1">{answeredCount} of {questions.length} answered</p>
        </div>
        <button
          onClick={finishInterview}
          disabled={processing || answeredCount === 0}
          className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 transition-colors"
        >
          Finish Interview
        </button>
      </div>

      <div className="w-full bg-gray-200 rounded-full h-2">
        <div className="bg-blue-600 h-2 rounded-full transition-all duration-500" style={{ width: progress + '%' }} />
      </div>

      <div className="flex gap-2 flex-wrap">
        {questions.map((_, idx) => (
          <button
            key={idx}
            onClick={() => setCurrentIndex(idx)}
            className={"w-9 h-9 rounded-full text-xs font-bold transition-colors " + (
              idx === currentIndex ? 'bg-blue-600 text-white ring-2 ring-blue-300' :
              answered[idx] ? 'bg-green-500 text-white' :
              'bg-gray-200 text-gray-600 hover:bg-gray-300'
            )}
          >
            {idx + 1}
          </button>
        ))}
      </div>

      {currentQuestion && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 space-y-6">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-blue-600 font-bold">{currentIndex + 1}</span>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3 flex-wrap">
                <span className={"px-2 py-0.5 rounded text-xs font-medium " + (
                  currentQuestion.difficulty === 'easy' ? 'bg-green-100 text-green-700' :
                  currentQuestion.difficulty === 'hard' ? 'bg-red-100 text-red-700' :
                  'bg-yellow-100 text-yellow-700'
                )}>{currentQuestion.difficulty}</span>
                <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs font-medium">{currentQuestion.question_type}</span>
                {currentQuestion.skill_tag && (
                  <span className="px-2 py-0.5 bg-blue-100 text-blue-600 rounded text-xs font-medium">{currentQuestion.skill_tag}</span>
                )}
              </div>
              <p className="text-lg text-gray-900 leading-relaxed">{currentQuestion.text}</p>
            </div>
          </div>

          <button onClick={playQuestion} disabled={audioPlaying}
            className={"flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors " + (
              audioPlaying ? 'bg-purple-200 text-purple-500 cursor-not-allowed' :
              audioError ? 'bg-red-100 text-red-600 hover:bg-red-200' :
              'bg-purple-100 text-purple-700 hover:bg-purple-200'
            )}>
            {audioPlaying ? '?? Playing...' : audioError ? '?? Retry Audio' : '?? Listen to Question'}
          </button>

          <div className="border-t border-gray-100 pt-6">
            <p className="text-sm font-medium text-gray-700 mb-4">Your Answer</p>

            {!answered[currentIndex] ? (
              <div className="space-y-4">
                <div className={"flex items-center gap-3 p-4 rounded-xl border-2 " + (recording ? 'border-red-400 bg-red-50' : 'border-gray-200 bg-gray-50')}>
                  <div className={"w-4 h-4 rounded-full flex-shrink-0 " + (recording ? 'bg-red-500 animate-pulse' : 'bg-gray-300')} />
                  <div className="flex-1">
                    <span className="text-sm text-gray-700">
                      {recording ? 'Recording ' + recordingTime + 's — speak your answer clearly' :
                       processing ? 'Transcribing your answer — please wait...' :
                       'Click Start Recording, speak your answer, then click Stop'}
                    </span>
                  </div>
                  {recording && <span className="text-xs text-red-500 font-bold">LIVE</span>}
                </div>

                {!recording ? (
                  <button onClick={startRecording} disabled={processing}
                    className="w-full bg-red-500 text-white py-3 rounded-lg font-medium hover:bg-red-600 disabled:opacity-50 transition-colors flex items-center justify-center gap-2">
                    {processing ? '? Transcribing...' : '?? Start Recording'}
                  </button>
                ) : (
                  <button onClick={stopRecording}
                    className="w-full bg-gray-800 text-white py-3 rounded-lg font-medium hover:bg-gray-900 transition-colors flex items-center justify-center gap-2">
                    ? Stop Recording ({recordingTime}s)
                  </button>
                )}
                <p className="text-xs text-gray-400 text-center">Speak clearly for at least 5 seconds. Minimum 2 seconds required.</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium text-green-800">Answer recorded</p>
                    <button
                      onClick={() => setAnswered(prev => { const n = {...prev}; delete n[currentIndex]; return n })}
                      className="text-xs text-red-500 hover:text-red-600 font-medium"
                    >
                      Re-record
                    </button>
                  </div>
                  <p className="text-sm text-gray-700">{answered[currentIndex].transcribed_text}</p>
                </div>

                <div className="flex gap-3">
                  {currentIndex > 0 && (
                    <button onClick={prevQuestion}
                      className="flex-1 border border-gray-200 text-gray-700 py-3 rounded-lg font-medium hover:bg-gray-50 transition-colors">
                      Previous
                    </button>
                  )}
                  {currentIndex < questions.length - 1 ? (
                    <button onClick={nextQuestion}
                      className="flex-1 bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors">
                      Next Question
                    </button>
                  ) : (
                    <button onClick={finishInterview} disabled={processing}
                      className="flex-1 bg-green-600 text-white py-3 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 transition-colors">
                      {processing ? 'Generating Report...' : 'Finish and Get Results'}
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

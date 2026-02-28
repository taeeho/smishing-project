import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

const INPUT_TABS = [
  { key: 'image', label: '캡처 이미지', icon: '📷' },
  { key: 'text', label: '문자 텍스트', icon: '💬' },
  { key: 'url', label: '의심 URL', icon: '🔗' },
]

export default function HomePage() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('image')
  const [text, setText] = useState('')
  const [url, setUrl] = useState('')
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const fileRef = useRef()

  const handleFile = (e) => {
    const f = e.target.files?.[0]
    if (!f) return
    setFile(f)
    const reader = new FileReader()
    reader.onload = (ev) => setPreview(ev.target.result)
    reader.readAsDataURL(f)
  }

  const removeFile = () => {
    setFile(null)
    setPreview(null)
  }

  const canSubmit = !loading && (
    activeTab === 'image' ? !!file : activeTab === 'url' ? url.trim() : text.trim()
  )

  const onSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      let response

      if (activeTab === 'image' && file) {
        const formData = new FormData()
        formData.append('file', file)
        response = await axios.post('/api/analyze/image', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
      } else if (activeTab === 'url' && url.trim()) {
        response = await axios.post('/api/analyze/url', { url: url.trim() })
      } else if (activeTab === 'text' && text.trim()) {
        response = await axios.post('/api/analyze/text', { text: text.trim() })
      }

      if (response) {
        navigate('/result', { state: { result: response.data } })
      }
    } catch (err) {
      setError('분석 중 오류가 발생했어요. 다시 시도해 주세요.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-4">
      {/* 헤더 영역 */}
      <div className="text-center pt-3">
        <div className="mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-400 to-purple-500 text-2xl shadow-lg shadow-violet-200">
          🔍
        </div>
        <h1 className="text-2xl font-extrabold text-slate-800">의심 문자 분석</h1>
        <p className="mt-1 text-sm text-slate-500">아래 3가지 중 하나만 입력해도 분석할 수 있어요</p>
      </div>

      {/* 입력 방식 탭 */}
      <div className="rounded-2xl bg-white/90 p-1 shadow-sm ring-1 ring-violet-100">
        <div className="grid grid-cols-3 gap-1">
          {INPUT_TABS.map((tab) => {
            const isActive = activeTab === tab.key
            return (
              <button
                key={tab.key}
                type="button"
                onClick={() => setActiveTab(tab.key)}
                className={[
                  'flex flex-col items-center gap-1 rounded-xl px-2 py-2 text-xs font-semibold transition',
                  isActive
                    ? 'bg-white text-violet-700 shadow-sm'
                    : 'text-slate-500 hover:text-violet-600',
                ].join(' ')}
              >
                <span className="text-lg">{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            )
          })}
        </div>
      </div>

      <form onSubmit={onSubmit} className="flex flex-col gap-4">
        {/* ── 1. 이미지 업로드 ──────────────────────────── */}
        {activeTab === 'image' && (
          <div className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-violet-100">
            <label className="mb-2 flex items-center gap-1 text-sm font-semibold text-slate-600">
              📷 캡처 이미지
            </label>
            {preview ? (
              <div className="relative">
                <img
                  src={preview}
                  alt="미리보기"
                  className="h-40 w-full rounded-xl bg-slate-50 object-contain"
                />
                <button
                  type="button"
                  onClick={removeFile}
                  className="absolute right-2 top-2 flex h-6 w-6 items-center justify-center rounded-full bg-slate-900/70 text-xs text-white"
                >
                  ✕
                </button>
              </div>
            ) : (
              <div
                onClick={() => fileRef.current?.click()}
                className="cursor-pointer rounded-xl border border-dashed border-violet-200 bg-violet-50/40 px-4 py-6 text-center transition hover:border-violet-300"
              >
                <span className="mb-1 block text-2xl">📤</span>
                <span className="text-sm text-slate-500">탭하여 이미지 업로드</span>
              </div>
            )}
            <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={handleFile} />
          </div>
        )}

        {/* ── 2. 문자 텍스트 ───────────────────────────── */}
        {activeTab === 'text' && (
          <div className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-violet-100">
            <label className="mb-2 flex items-center gap-1 text-sm font-semibold text-slate-600">
              💬 문자 텍스트
            </label>
            <textarea
              rows={4}
              placeholder="의심 문자 내용을 붙여넣으세요"
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="w-full resize-none rounded-xl border border-violet-200 bg-white px-4 py-3 text-sm text-slate-700 placeholder:text-slate-400 focus:border-violet-400 focus:outline-none focus:ring-2 focus:ring-violet-200"
            />
          </div>
        )}

        {/* ── 3. URL 입력 ──────────────────────────────── */}
        {activeTab === 'url' && (
          <div className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-violet-100">
            <label className="mb-2 flex items-center gap-1 text-sm font-semibold text-slate-600">
              🔗 의심 URL
            </label>
            <input
              placeholder="https://..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full rounded-xl border border-violet-200 bg-white px-4 py-3 text-sm text-slate-700 placeholder:text-slate-400 focus:border-violet-400 focus:outline-none focus:ring-2 focus:ring-violet-200"
            />
          </div>
        )}

        {/* 에러 */}
        {error && (
          <div className="rounded-xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-600">
            ⚠️ {error}
          </div>
        )}

        {/* 분석 버튼 */}
        <button
          type="submit"
          disabled={!canSubmit}
          className="flex w-full items-center justify-center gap-2 rounded-2xl bg-violet-600 px-4 py-3 text-base font-semibold text-white shadow-sm transition hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />
              AI 분석 중...
            </span>
          ) : (
            '🔍 분석 시작'
          )}
        </button>
      </form>

      {/* 안내 */}
      <div className="grid grid-cols-3 gap-2 pt-1">
        {[
          { icon: '🤖', title: 'AI 분류' },
          { icon: '📊', title: '근거 제시' },
          { icon: '🛡️', title: '행동 가이드' },
        ].map((c) => (
          <div
            key={c.title}
            className="rounded-xl border border-violet-100 bg-white px-2 py-3 text-center"
          >
            <div className="mb-1 text-lg">{c.icon}</div>
            <div className="text-xs font-semibold text-slate-500">{c.title}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

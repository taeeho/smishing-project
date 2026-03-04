import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

const INPUT_TABS = [
  { key: 'image', label: '이미지', icon: '📷', desc: '캡처 이미지 업로드' },
  { key: 'text', label: '텍스트', icon: '💬', desc: '의심 문자 붙여넣기' },
  { key: 'url', label: 'URL', icon: '🔗', desc: '의심 링크 입력' },
  { key: 'qr', label: 'QR', icon: '🔳', desc: 'QR 이미지 분석' },
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
    if(!f) return
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
    activeTab === 'image' || activeTab === 'qr'
      ? !!file
      : activeTab === 'url'
        ? url.trim()
        : text.trim()
  )

  const onSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      let response
      const token = localStorage.getItem('access_token')
      const authHeader = token ? { Authorization: `Bearer ${token}` } : {}

      if ((activeTab === 'image' || activeTab === 'qr') && file) {
        const formData = new FormData()
        formData.append('file', file)
        response = await axios.post('/api/analyze/image', formData, {
          headers: { ...authHeader, 'Content-Type': 'multipart/form-data' },
        })
      } else if (activeTab === 'url' && url.trim()) {
        response = await axios.post('/api/analyze/url', { url: url.trim() }, { headers: authHeader })
      } else if (activeTab === 'text' && text.trim()) {
        response = await axios.post('/api/analyze/text', { text: text.trim() }, { headers: authHeader })
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
    <div className="space-y-6">
      <section className="rounded-[28px] border border-[#eadfd5] bg-[#f8f1ea] px-5 py-6 shadow-sm">
        <p className="text-xs font-semibold text-violet-500">Q체크 스마트 분석</p>
        <h1 className="mt-2 text-2xl font-extrabold leading-tight text-[#2c2c2c]">의심 채팅을<br/>안전하게 확인하세요</h1>
        <p className="mt-2 text-sm text-[#6b6b6b]">채팅 내용을 그대로 가져오면 위험도를 알려드립니다.</p>

        <div className="mt-6 flex justify-center">
          <div className="relative w-[240px] rounded-[36px] border border-[#eadfd5] bg-[#f6efe8] p-4 shadow">
            <div className="absolute left-1/2 top-2 h-2 w-16 -translate-x-1/2 rounded-full bg-[#e9e1d9]" />
            <div className="mt-4 space-y-3 rounded-[24px] bg-white px-4 py-4 shadow-sm">
              <div className="max-w-[170px] rounded-2xl bg-[#efe9ff] px-3 py-2 text-[11px] text-[#5f4fc6]">[공지] 계정 보호를 위해 링크를 확인해주세요.</div>
              <div className="ml-auto max-w-[170px] rounded-2xl bg-[#f7f2ec] px-3 py-2 text-[11px] text-[#7a7067]">확인 링크가 진짜인지 모르겠어요.</div>
              <div className="max-w-[170px] rounded-2xl bg-[#efe9ff] px-3 py-2 text-[11px] text-[#5f4fc6]">아래 버튼으로 바로 검사해요.</div>
            </div>
          </div>
        </div>
      </section>

      <form onSubmit={onSubmit} className="space-y-4">
        <section className="rounded-2xl border border-[#eadfd5] bg-white p-3 shadow-sm">
          <div className="grid grid-cols-2 gap-2">
            {INPUT_TABS.map((tab) => {
              const isActive = activeTab === tab.key
              return (
                <button
                  key={tab.key}
                  type="button"
                  onClick={() => setActiveTab(tab.key)}
                  className={[
                    'rounded-2xl px-3 py-3 text-left transition',
                    isActive
                      ? 'bg-[#efe9ff] text-[#6b5ad3]'
                      : 'bg-[#f9f4ef] text-[#6b6b6b] hover:bg-[#efe9ff]',
                  ].join(' ')}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-xl">{tab.icon}</span>
                    <span className="text-sm font-semibold">{tab.label}</span>
                  </div>
                  <p className="mt-1 text-[11px] text-[#8c827a]">{tab.desc}</p>
                </button>
              )
            })}
          </div>
        </section>

        {(activeTab === 'image' || activeTab === 'qr') && (
          <div className="rounded-2xl border border-[#eadfd5] bg-white p-5 shadow-sm">
            <label className="mb-2 flex items-center gap-1 text-sm font-semibold text-[#6b6b6b]">
              {activeTab === 'qr' ? '🔳 QR 이미지' : '📷 캡처 이미지'}
            </label>
            {preview ? (
              <div className="relative">
                <img
                  src={preview}
                  alt="미리보기"
                  className="h-44 w-full rounded-xl bg-[#faf6f2] object-contain"
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
                className="cursor-pointer rounded-xl border border-dashed border-[#e7dcd2] bg-[#faf6f2] px-4 py-8 text-center transition hover:border-[#d9cdc2]"
              >
                <span className="mb-1 block text-2xl">📤</span>
                <span className="text-sm text-[#8a8077]">탭하여 이미지 업로드</span>
              </div>
            )}
            <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={handleFile} />
          </div>
        )}

        {activeTab === 'text' && (
          <div className="rounded-2xl border border-[#eadfd5] bg-white p-5 shadow-sm">
            <label className="mb-2 flex items-center gap-1 text-sm font-semibold text-[#6b6b6b]">
              💬 문자 텍스트
            </label>
            <textarea
              rows={5}
              placeholder="의심 문자 내용을 붙여넣으세요"
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="w-full resize-none rounded-xl border border-[#e7dcd2] bg-white px-4 py-3 text-sm text-[#3b3b3b] placeholder:text-[#9a9088] focus:border-[#b9aaf0] focus:outline-none focus:ring-2 focus:ring-[#cfc4ff]"
            />
          </div>
        )}

        {activeTab === 'url' && (
          <div className="rounded-2xl border border-[#eadfd5] bg-white p-5 shadow-sm">
            <label className="mb-2 flex items-center gap-1 text-sm font-semibold text-[#6b6b6b]">🔗 의심 URL</label>
            <input placeholder="https://..." value={url} onChange={(e) => setUrl(e.target.value)} className="w-full rounded-xl border border-[#e7dcd2] bg-white px-4 py-3 text-sm text-[#3b3b3b] placeholder:text-[#9a9088] focus:border-[#b9aaf0] focus:outline-none focus:ring-2 focus:ring-[#cfc4ff]" />
          </div>
        )}

        {error && (
          <div className="rounded-xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-600">⚠️ {error}</div>
        )}

        <button type="submit" disabled={!canSubmit} className="flex w-full items-center justify-center gap-2 rounded-2xl bg-[#8b73e5] px-4 py-4 text-base font-semibold text-white shadow-sm transition hover:bg-[#7a63db] disabled:cursor-not-allowed disabled:opacity-50">
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />분석 중...</span>
          ) : (
            '검사 시작하기'
          )}
        </button>
      </form>
    </div>
  )
}

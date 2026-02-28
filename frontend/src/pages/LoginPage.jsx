import { useState } from 'react'
import axios from 'axios'

export default function LoginPage() {
  const [authLoading, setAuthLoading] = useState(false)
  const [error, setError] = useState('')

  const handleKakaoLogin = async () => {
    setAuthLoading(true)
    setError('')
    try {
      const res = await axios.get('/api/auth/kakao/login')
      const { authorize_url } = res.data
      window.location.href = authorize_url
    } catch (err) {
      setError('카카오 로그인 준비에 실패했어요. 잠시 후 다시 시도해주세요.')
      setAuthLoading(false)
    }
  }

  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4">
      <div className="w-full max-w-[360px] rounded-[32px] border border-violet-100 bg-[#faf6f1] p-6 shadow-sm">
        <div className="flex flex-col items-center gap-4">
          <div className="mt-6 flex h-20 w-20 items-center justify-center rounded-3xl bg-white shadow-sm">
            <span className="text-4xl font-black text-violet-500">Q</span>
          </div>
          <div className="text-center">
            <h1 className="text-xl font-bold text-slate-800">로그인 방식</h1>
            <p className="mt-1 text-xs text-slate-500">원하는 방법으로 시작하세요</p>
          </div>
        </div>

        <div className="mt-10 space-y-3">
          <button
            type="button"
            disabled
            className="flex w-full items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-400"
          >
            <span className="flex items-center gap-2">
              <span className="text-lg">G</span>
              구글로 로그인하기
            </span>
            <span>›</span>
          </button>

          <button
            type="button"
            onClick={handleKakaoLogin}
            disabled={authLoading}
            className="flex w-full items-center justify-between rounded-2xl bg-violet-500 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-violet-600 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <span className="flex items-center gap-2">
              <span className="text-lg">▶</span>
              카카오로 시작하기
            </span>
            <span>›</span>
          </button>
        </div>

        {error && (
          <div className="mt-5 rounded-xl bg-rose-50 px-4 py-2 text-xs font-medium text-rose-600">
            {error}
          </div>
        )}
      </div>
    </div>
  )
}

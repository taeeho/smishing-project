import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function KakaoCallback() {
  const navigate = useNavigate()
  const [status, setStatus] = useState('카카오 로그인 처리 중...')
  const ranRef = useRef(false)

  useEffect(() => {
    if (ranRef.current) return
    ranRef.current = true

    const run = async () => {
      const params = new URLSearchParams(window.location.search)
      const code = params.get('code')

      if (!code) {
        setStatus('인증 코드가 없습니다. 다시 시도해주세요.')
        return
      }

      try {
        const res = await axios.get(`/api/auth/kakao/callback?code=${code}`)
        const { user, tokens } = res.data
        localStorage.setItem('auth_user', JSON.stringify(user))
        localStorage.setItem('access_token', tokens.access_token)
        localStorage.setItem('refresh_token', tokens.refresh_token)
        setStatus('로그인 완료! 홈으로 이동합니다.')
        setTimeout(() => {
          window.location.replace('/')
        }, 300)
      } catch (err) {
        setStatus('로그인에 실패했습니다. 이메일 제공 동의를 확인해주세요.')
      }
    }

    run()
  }, [navigate])

  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <div className="rounded-2xl bg-white px-6 py-8 text-center shadow-sm ring-1 ring-violet-100">
        <div className="mb-3 text-2xl">🟣</div>
        <p className="text-sm text-slate-600">{status}</p>
      </div>
    </div>
  )
}

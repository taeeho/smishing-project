import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import axios from 'axios'

const navItems = [
  { to: '/', label: '분석', icon: '🔍' },
  { to: '/trend', label: '트렌드', icon: '📈' },
  { to: '/history', label: '기록', icon: '🗂️' },
  { to: '/profile', label: '회원정보', icon: '👤' },
]

export default function Layout() {
  const navigate = useNavigate()
  const [userName, setUserName] = useState('')

  useEffect(()=>{
    const stored = localStorage.getItem('auth_user')
    if (stored) {
      try {
        const user = JSON.parse(stored)
        setUserName(user?.username || '')
      } catch {
        setUserName('')
      }
    }
  }, [])

  const handleLogout = async () => {
    const refresh = localStorage.getItem('refresh_token')
    try {
      if (refresh) {
        await axios.post(
          '/api/auth/logout',
          {},
          { headers: { Authorization: `Bearer ${refresh}` } },
        )
      }
    } catch {
    } finally {
      localStorage.removeItem('auth_user')
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      setUserName('')
      navigate('/login')
    }
  }

  return (
    <div className="mx-auto flex min-h-[100dvh] w-full max-w-[393px] flex-col bg-violet-50">
      {/* 상단 */}
      <header className="sticky top-0 z-40 border-b border-violet-100 bg-white/90 px-4 py-3 backdrop-blur">
        <div className="flex items-center justify-between">
          <NavLink to="/" className="flex items-center gap-2 no-underline">
            <span className="text-lg font-extrabold text-violet-600">Q체크</span>
          </NavLink>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2 rounded-xl border border-violet-100 bg-violet-50 px-3 py-1.5 text-xs text-slate-700">
              <span className="text-sm">👤</span>
              <span>{userName ? `${userName}님` : ''}</span>
            </div>
            {userName ? (
              <button type="button" onClick={handleLogout} className="rounded-xl border border-violet-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-violet-50">로그아웃</button>
            ) : (
              <button type="button" onClick={() => navigate('/login')} className="rounded-xl bg-violet-600 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-violet-700">로그인</button>
            )}
          </div>
        </div>
      </header>

      {/* 콘텐츠 */}
      <main className="flex-1 px-4 pb-24 pt-4">
        <Outlet />
      </main>

      {/* 하단 */}
      <nav className="fixed bottom-3 left-1/2 z-50 w-[calc(100%-2rem)] max-w-[360px] -translate-x-1/2 rounded-3xl border border-violet-100 bg-white/95 px-4 py-2 shadow-lg backdrop-blur">
        <div className="flex items-center justify-between">
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to === '/'} className={({ isActive }) => ['flex flex-1 flex-col items-center gap-1 rounded-2xl px-2 py-2 text-[11px] font-semibold transition-colors', isActive ? 'text-violet-600' : 'text-slate-500',].join(' ')}>
              <span className="text-xl">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  )
}

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function HistoryPage() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [items, setItems] = useState([])
  const [deletingId, setDeletingId] = useState(null)
  const navigate = useNavigate()

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setError('로그인이 필요합니다.')
        setLoading(false)
        return
      }
      const res = await axios.get('/api/analyze/history', {
        headers: { Authorization: `Bearer ${token}` },
      })
      setItems(res.data.results || [])
    } catch (err) {
      setError('기록을 불러오지 못했습니다.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const badgeClass = (status) =>
    status === '위험'
      ? 'bg-rose-100 text-rose-700 border-rose-200'
      : 'bg-emerald-100 text-emerald-700 border-emerald-200'

  const openDetail = async (analysisId) => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setError('로그인이 필요합니다.')
        return
      }
      const res = await axios.get(`/api/analyze/history/${analysisId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      navigate('/result', { state: { result: res.data } })
    } catch (err) {
      setError('상세 정보를 불러오지 못했습니다.')
    }
  }

  const deleteItem = async (analysisId) => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setError('로그인이 필요합니다.')
        return
      }
      setDeletingId(analysisId)
      await axios.delete(`/api/analyze/history/${analysisId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      setItems((prev) => prev.filter((item) => item.analysis_id !== analysisId))
    } catch (err) {
      setError('삭제에 실패했습니다.')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="space-y-6">
      <header className="rounded-2xl border border-violet-100 bg-white p-5 shadow-sm">
        <h1 className="text-xl font-bold text-slate-800">기록</h1>
        <p className="mt-1 text-sm text-slate-500">내가 올렸던 분석 기록을 모아봅니다.</p>
      </header>

      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-violet-200 border-t-violet-600" />
        </div>
      )}
      {error && !loading && (
        <div className="rounded-xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-600">
          {error}
        </div>
      )}

      {!loading && !error && items.length === 0 && (
        <div className="rounded-2xl border border-violet-100 bg-white px-4 py-10 text-center text-sm text-slate-400">
          아직 기록이 없어요.
        </div>
      )}

      {!loading && !error && items.length > 0 && (
        <section className="space-y-3">
          {items.map((item) => (
            <div
              key={item.analysis_id}
              className="rounded-2xl border border-violet-100 bg-white px-4 py-4 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <button
                  type="button"
                  onClick={() => openDetail(item.analysis_id)}
                  className="text-left"
                >
                  <p className="text-sm font-semibold text-slate-700">{item.title}</p>
                  <p className="text-xs text-slate-400">위험도 {Math.round(item.risk_score)}%</p>
                </button>
                <div className="flex items-center gap-2">
                  <span className={`rounded-full border px-3 py-1 text-xs font-bold ${badgeClass(item.status)}`}>
                    {item.status}
                  </span>
                  <button
                    type="button"
                    onClick={() => deleteItem(item.analysis_id)}
                    disabled={deletingId === item.analysis_id}
                    className="rounded-lg border border-rose-200 px-2 py-1 text-[11px] font-semibold text-rose-600 transition hover:bg-rose-50 disabled:opacity-50"
                  >
                    {deletingId === item.analysis_id ? '삭제중' : '삭제'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </section>
      )}
    </div>
  )
}

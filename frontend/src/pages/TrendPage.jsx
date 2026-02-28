import { useEffect, useState } from 'react'
import axios from 'axios'

const AGE_GROUPS = ['10대', '20대', '30대', '40대', '미공개']

export default function TrendPage() {
  const [activeAge, setActiveAge] = useState('10대')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [items, setItems] = useState([])
  const [range, setRange] = useState({ start: '', end: '' })

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError('')
      try {
        const res = await axios.get('/api/analyze/trends', {
          params: { age_group: activeAge },
        })
        setItems(res.data.results || [])
        setRange({ start: res.data.start_date || '', end: res.data.end_date || '' })
      } catch (err) {
        setError('트렌드 정보를 불러오지 못했습니다.')
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [activeAge])

  return (
    <div className="space-y-6">
      <header className="rounded-2xl border border-violet-100 bg-white p-5 shadow-sm">
        <h1 className="text-xl font-bold text-slate-800">트렌드</h1>
        <p className="mt-1 text-sm text-slate-500">
          최근 1년 동안 사용자들이 자주 겪은 스미싱 유형을 모아 보여줍니다.
        </p>
      </header>

      <section className="rounded-2xl border border-violet-100 bg-white p-5 shadow-sm">
        <h2 className="text-sm font-semibold text-slate-600">나이대 선택</h2>
        <div className="mt-3 grid grid-cols-3 gap-2">
          {AGE_GROUPS.map((age) => (
            <button
              key={age}
              type="button"
              onClick={() => setActiveAge(age)}
              className={[
                'rounded-xl border px-3 py-2 text-xs font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-300',
                activeAge === age
                  ? 'border-violet-200 bg-violet-100 text-violet-700'
                  : 'border-violet-100 bg-violet-50 text-slate-600 hover:border-violet-200 hover:bg-violet-100 hover:text-violet-600',
              ].join(' ')}
            >
              {age}
            </button>
          ))}
        </div>
      </section>

      <section className="rounded-2xl border border-violet-100 bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-600">최근 1년 TOP 10</h2>
          <span className="text-xs text-slate-400">{range.start} ~ {range.end}</span>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-6">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-violet-200 border-t-violet-600" />
          </div>
        )}

        {error && !loading && (
          <div className="mt-4 rounded-xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-600">
            {error}
          </div>
        )}

        {!loading && !error && items.length === 0 && (
          <div className="mt-4 rounded-xl border border-violet-100 bg-violet-50/40 px-4 py-8 text-center text-sm text-slate-400">
            표시할 트렌드 데이터가 없습니다.
          </div>
        )}

        {!loading && !error && items.length > 0 && (
          <div className="mt-4 space-y-3">
            {items.map((item, idx) => (
              <div
                key={`${item.label}-${idx}`}
                className="flex items-center justify-between rounded-xl border border-violet-100 bg-violet-50/60 px-4 py-3"
              >
                <div className="flex items-center gap-3">
                  <span className="flex h-7 w-7 items-center justify-center rounded-full bg-white text-xs font-bold text-violet-600">
                    {idx + 1}
                  </span>
                  <div>
                    <p className="text-sm font-semibold text-slate-700">{item.label}</p>
                    <p className="text-xs text-slate-400">{item.count}건</p>
                  </div>
                </div>
                <span className="text-xs font-semibold text-slate-500">유사도 {item.similarity}%</span>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}

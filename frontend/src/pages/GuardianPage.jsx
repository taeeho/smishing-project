import { useEffect, useState } from 'react'
import axios from 'axios'

const STATUS_COLORS = {
  '미조치': 'bg-rose-100 text-rose-700 border-rose-200',
  '확인중': 'bg-amber-100 text-amber-700 border-amber-200',
  '완료': 'bg-violet-100 text-violet-700 border-violet-200',
}

const RISK_COLORS = {
  '높음': 'border-l-rose-500',
  '중간': 'border-l-amber-400',
  '낮음': 'border-l-emerald-400',
}

export default function GuardianPage() {
  const [cases, setCases] = useState([])
  const [summary, setSummary] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [editMemo, setEditMemo] = useState({})

  const fetchData = async () => {
    setLoading(true)
    try{
      const [casesRes, summaryRes, alertsRes] = await Promise.all([
        axios.get('/api/guardian/cases'),
        axios.get('/api/guardian/summary'),
        axios.get('/api/guardian/alerts'),
      ])
      setCases(casesRes.data.cases || [])
      setSummary(summaryRes.data)
      setAlerts(alertsRes.data.alerts || [])
    } catch(err){
      console.error('보호자 데이터 로드 실패', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  const updateStatus = async (caseId, status) => {
    try {
      await axios.patch(`/api/guardian/case/${caseId}/status`, { status })
      fetchData()
    } catch (err) {
      console.error('상태 업데이트 실패', err)
    }
  }

  const saveMemo = async (caseId) => {
    try{
      await axios.post('/api/guardian/memo', { case_id: caseId, memo: editMemo[caseId] || '' })
      setEditMemo((prev) => ({ ...prev, [caseId]: undefined }))
      fetchData()
    } catch (err) {
      console.error('메모 저장 실패', err)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-violet-200 border-t-violet-600" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* 헤더 */}
      <header className="text-center">
        <div className="mb-4 inline-flex h-20 w-20 items-center justify-center rounded-3xl bg-gradient-to-br from-violet-400 to-purple-600 text-4xl shadow-xl shadow-violet-200">
          🛡️
        </div>
        <h1 className="text-3xl font-bold">보호자 모드</h1>
        <p className="mt-2 text-lg text-slate-500">
          가족의 스미싱 분석 결과를 한눈에 확인하고 조치하세요
        </p>
      </header>

      {/* 하루 요약 */}
      {summary && (
        <div className="grid gap-4 sm:grid-cols-4">
          {[
            { label: '전체', value: summary.total_cases, color: 'bg-violet-50 text-violet-700' },
            { label: '위험', value: summary.high_risk_count, color: 'bg-rose-100 text-rose-700' },
            { label: '주의', value: summary.medium_risk_count, color: 'bg-amber-100 text-amber-700' },
            { label: '미조치', value: summary.unresolved_count, color: 'bg-violet-100 text-violet-700' },
          ].map((stat) => (
            <div key={stat.label} className={`rounded-2xl p-5 text-center ${stat.color}`}>
              <p className="text-3xl font-bold">{stat.value}</p>
              <p className="text-sm font-semibold">{stat.label}</p>
            </div>
          ))}
        </div>
      )}

      {/* 알림 */}
      {alerts.length > 0 && (
        <div className="space-y-2">
          {alerts.map((alert, i) => (
            <div key={i} className="flex items-center gap-3 rounded-xl border border-rose-200 bg-rose-50 p-4">
              <span className="text-xl">🚨</span>
              <p className="text-sm font-medium text-rose-700">{alert.message}</p>
            </div>
          ))}
        </div>
      )}

      {/* 케이스 목록 */}
      <section>
        <h2 className="mb-4 text-xl font-bold">케이스 목록</h2>
        {cases.length === 0 ? (
          <div className="rounded-2xl border-2 border-dashed border-violet-200 p-10 text-center text-slate-400">
            분석된 케이스가 없어요.
          </div>
        ) : (
          <div className="space-y-4">
            {cases.map((c) => (
              <div
                key={c.case_id}
                className={`rounded-2xl border border-violet-100 border-l-4 bg-white p-6 shadow-md transition hover:shadow-lg ${RISK_COLORS[c.risk_level] || ''}`}
              >
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-bold">{c.summary}</h3>
                      <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-500">#{c.case_id}</span>
                    </div>
                    <p className="mt-1 text-sm text-slate-500">유형: {c.smishing_type} · {c.created_at}</p>
                    <p className="mt-2 text-slate-600">{c.guardian_summary}</p>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className={`rounded-full border px-3 py-1 text-xs font-bold ${STATUS_COLORS[c.status] || ''}`}>{c.status}</span>
                    <select value={c.status} onChange={(e) => updateStatus(c.case_id, e.target.value)} className="rounded-lg border border-violet-200 px-2 py-1 text-sm focus:border-violet-400 focus:outline-none">
                      <option value="미조치">미조치</option>
                      <option value="확인중">확인중</option>
                      <option value="완료">완료</option>
                    </select>
                  </div>
                </div>

                {/* 메모 */}
                <div className="mt-4 border-t border-violet-100 pt-4">
                  <label className="text-sm font-semibold text-slate-500">📝 메모</label>
                  <div className="mt-2 flex gap-2">
                    <input
                      placeholder="메모를 입력하세요..."
                      value={editMemo[c.case_id] !== undefined ? editMemo[c.case_id] : c.memo}
                      className="flex-1 rounded-xl border border-violet-200 px-4 py-2 text-sm focus:border-violet-400 focus:outline-none"
                      onChange={(e) =>
                        setEditMemo((prev) => ({ ...prev, [c.case_id]: e.target.value }))
                      }/>
                    <button onClick={() => saveMemo(c.case_id)} className="rounded-xl bg-violet-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-violet-700">저장</button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
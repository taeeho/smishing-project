import { useLocation, useNavigate } from 'react-router-dom'

function RiskBadge({ label }) {
  const colors = {
    '높음': 'bg-rose-100 text-rose-700 border-rose-200',
    '중간': 'bg-amber-100 text-amber-700 border-amber-200',
    '낮음': 'bg-emerald-100 text-emerald-700 border-emerald-200',
    '정보 부족': 'bg-slate-100 text-slate-500 border-slate-200',
  }
  return (
    <span className={`inline-block rounded-full border px-3 py-1 text-sm font-bold ${colors[label] || colors['정보 부족']}`}>
      {label}
    </span>
  )
}

export default function ResultPage() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const r = state?.result

  if (!r) {
    return (
      <div className="py-20 text-center">
        <p className="text-xl text-slate-500">분석 결과가 없어요.</p>
        <button onClick={() => navigate('/')} className="mt-4 rounded-xl bg-violet-600 px-6 py-3 font-semibold text-white">
          분석하러 가기
        </button>
      </div>
    )
  }

  const riskColor = {
    '높음': 'from-rose-500 to-red-600',
    '중간': 'from-amber-400 to-orange-500',
    '낮음': 'from-emerald-400 to-teal-500',
  }[r.url_risk_label] || 'from-violet-400 to-purple-600'

  return (
    <div className="space-y-6">
      {/* 위험도 헤더 */}
      <div className={`rounded-3xl bg-gradient-to-r ${riskColor} p-8 text-white shadow-2xl`}>
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white/20 text-3xl backdrop-blur">
            {r.url_risk_label === '높음' ? '🚨' : r.url_risk_label === '중간' ? '⚠️' : '✅'}
          </div>
          <div>
            <h1 className="text-2xl font-bold">위험 요약</h1>
            <p className="mt-1 text-lg text-white/90">{r.risk_summary}</p>
          </div>
        </div>
        <div className="mt-4 flex flex-wrap gap-3">
          <RiskBadge label={r.url_risk_label} />
          {r.smishing_type && r.smishing_type !== '판별불가' && (
            <span className="rounded-full border border-white/30 bg-white/10 px-3 py-1 text-sm font-semibold">
              유형: {r.smishing_type}
            </span>
          )}
          {r.group_risk && (
            <span className="rounded-full border border-white/30 bg-white/10 px-3 py-1 text-sm font-semibold">
              📈 집단 위험 감지
            </span>
          )}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* 근거 제시 */}
        <section className="rounded-2xl border border-violet-100 bg-white p-6 shadow-lg">
          <h2 className="mb-4 flex items-center gap-2 text-xl font-bold">
            <span className="text-2xl">📋</span> 근거 제시
          </h2>
          <ul className="space-y-2">
            {r.evidence?.map((ev, i) => (
              <li key={i} className="flex items-start gap-3 rounded-xl bg-violet-50/70 px-4 py-3">
                <span className="mt-0.5 text-violet-500">●</span>
                <span className="text-slate-700">{ev}</span>
              </li>
            ))}
          </ul>
          {r.similar_cases && (
            <div className="mt-4 rounded-xl bg-amber-50 p-4 text-sm text-amber-700">
              📊 <strong>유사 사례:</strong> {r.similar_cases}
            </div>
          )}
        </section>

        {/* 지금 할 행동 */}
        <section className="rounded-2xl border border-violet-100 bg-white p-6 shadow-lg">
          <h2 className="mb-4 flex items-center gap-2 text-xl font-bold">
            <span className="text-2xl">🚀</span> 지금 할 행동
          </h2>
          <ul className="space-y-2">
            {r.recommended_actions?.map((action, i) => (
              <li key={i} className="flex items-start gap-3 rounded-xl bg-violet-50/70 px-4 py-3">
                <span className="mt-0.5 text-lg">{i === 0 ? '❌' : i === 3 ? '📞' : '✅'}</span>
                <span className="font-medium text-slate-700">{action}</span>
              </li>
            ))}
          </ul>
        </section>

        {/* URL 분석 상세 */}
        {r.url_analyses?.length > 0 && (
          <section className="rounded-2xl border border-violet-100 bg-white p-6 shadow-lg">
            <h2 className="mb-4 flex items-center gap-2 text-xl font-bold">
              <span className="text-2xl">🔗</span> URL 분석 상세
            </h2>
            <div className="space-y-3">
              {r.url_analyses.map((ua, i) => (
                <div key={i} className="flex items-center justify-between rounded-xl border border-violet-100 bg-violet-50/70 px-4 py-3">
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-mono text-slate-600">{ua.url}</p>
                  </div>
                  <div className="ml-4 flex items-center gap-2">
                    <RiskBadge label={ua.risk_label} />
                    <span className="text-sm font-bold text-slate-500">{ua.risk_score}%</span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* 신고 문구 (복붙용) */}
        <section className="rounded-2xl border border-violet-100 bg-white p-6 shadow-lg">
          <h2 className="mb-4 flex items-center gap-2 text-xl font-bold">
            <span className="text-2xl">📝</span> 신고 문구 (복붙용)
          </h2>
          <div className="relative">
            <pre className="whitespace-pre-wrap rounded-xl bg-violet-950 p-5 text-sm leading-relaxed text-violet-100">
              {r.report_template}
            </pre>
            <button
              onClick={() => navigator.clipboard?.writeText(r.report_template)}
              className="absolute right-3 top-3 rounded-lg bg-white/10 px-3 py-1.5 text-xs font-semibold text-white backdrop-blur transition hover:bg-white/20"
            >
              📋 복사
            </button>
          </div>
          {r.report_procedure && (
            <p className="mt-3 text-sm text-slate-500">
              <strong>신고 절차:</strong> {r.report_procedure}
            </p>
          )}
        </section>
      </div>

      {/* 보호자 공유 요약 */}
      {r.guardian_summary && (
        <section className="rounded-2xl border-2 border-violet-200 bg-violet-50 p-6">
          <h2 className="mb-2 flex items-center gap-2 text-xl font-bold text-violet-800">
            <span className="text-2xl">🛡️</span> 보호자 공유 요약
          </h2>
          <p className="text-lg text-violet-700">{r.guardian_summary}</p>
          <button
            onClick={() => navigator.clipboard?.writeText(r.guardian_summary)}
            className="mt-3 rounded-xl bg-violet-600 px-5 py-2 text-sm font-semibold text-white transition hover:bg-violet-700"
          >
            📋 요약 복사하여 공유
          </button>
        </section>
      )}

      {/* FAQ */}
      {r.faq?.length > 0 && (
        <section className="rounded-2xl border border-violet-100 bg-white p-6 shadow-lg">
          <h2 className="mb-4 flex items-center gap-2 text-xl font-bold">
            <span className="text-2xl">❓</span> 자주 묻는 질문
          </h2>
          <div className="space-y-3">
            {r.faq.map((f, i) => (
              <div key={i} className="rounded-xl bg-violet-50/70 p-4">
                <p className="font-bold text-slate-800">Q. {f.q}</p>
                <p className="mt-1 text-slate-600">A. {f.a}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 하단 버튼 */}
      <div className="flex flex-wrap justify-center gap-4 pt-4">
        <button
          onClick={() => navigate('/')}
          className="rounded-2xl border-2 border-violet-200 px-8 py-3 font-semibold text-slate-700 transition hover:border-violet-300 hover:bg-violet-50"
        >
          🔍 새로운 분석
        </button>
        <button
          onClick={() => navigate('/coaching', { state: { result: r } })}
          className="rounded-2xl bg-gradient-to-r from-violet-600 to-purple-600 px-8 py-3 font-semibold text-white shadow-lg transition hover:shadow-xl"
        >
          📋 이후 대처 코칭 보기
        </button>
      </div>
    </div>
  )
}

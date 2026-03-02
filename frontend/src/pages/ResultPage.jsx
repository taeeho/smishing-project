import { useLocation, useNavigate } from 'react-router-dom'

function RiskBadge({ label }) {
  const colors = {
    '높음': 'bg-rose-100 text-rose-700 border-rose-200',
    '중간': 'bg-amber-100 text-amber-700 border-amber-200',
    '낮음': 'bg-emerald-100 text-emerald-700 border-emerald-200',
    '안전': 'bg-emerald-100 text-emerald-700 border-emerald-200',
    '정보 부족': 'bg-slate-100 text-slate-500 border-slate-200',
  }
  return (
    <span className={`inline-block rounded-full border px-3 py-1 text-xs font-bold ${colors[label] || colors['정보 부족']}`}>
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
    '안전': 'from-emerald-400 to-teal-500',
  }[r.url_risk_label] || 'from-violet-400 to-purple-600'

  return (
    <div className="space-y-5">
      {/* 위험도 헤더 */}
      <div className={`rounded-3xl bg-gradient-to-r ${riskColor} px-5 py-6 text-white shadow-xl`}>
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/20 text-2xl backdrop-blur">
            {r.url_risk_label === '높음' ? '🚨' : r.url_risk_label === '중간' ? '⚠️' : '✅'}
          </div>
          <div className="min-w-0">
            <h1 className="text-lg font-bold">위험 요약</h1>
            <p className="mt-1 text-sm text-white/90 line-clamp-2">{r.risk_summary}</p>
          </div>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          <RiskBadge label={r.url_risk_label} />
          {r.smishing_type && r.smishing_type !== '판별불가' && (
            <span className="rounded-full border border-white/30 bg-white/10 px-3 py-1 text-xs font-semibold">
              유형: {r.smishing_type}
            </span>
          )}
          {r.group_risk && (
            <span className="rounded-full border border-white/30 bg-white/10 px-3 py-1 text-xs font-semibold">
              📈 집단 위험 감지
            </span>
          )}
        </div>
      </div>

      {/* 근거 제시 */}
      <section className="rounded-2xl border border-violet-100 bg-white px-4 py-5 shadow-sm">
        <h2 className="mb-3 flex items-center gap-2 text-base font-bold text-slate-800">
          <span className="text-lg">📋</span> 근거 제시
        </h2>
        <ul className="space-y-2">
          {r.evidence?.map((ev, i) => (
            <li key={i} className="flex items-start gap-3 rounded-xl bg-violet-50/70 px-3 py-2">
              <span className="mt-0.5 text-violet-500">●</span>
              <span className="text-sm text-slate-700">{ev}</span>
            </li>
          ))}
        </ul>
        {r.similar_cases && (
          <div className="mt-3 rounded-xl bg-amber-50 px-4 py-3 text-xs text-amber-700">
            📊 <strong>유사 사례:</strong> {r.similar_cases}
          </div>
        )}
      </section>

      {/* 지금 할 행동 (안전이면 숨김) */}
      {r.url_risk_label !== '안전' && (
        <section className="rounded-2xl border border-violet-100 bg-white px-4 py-5 shadow-sm">
          <h2 className="mb-3 flex items-center gap-2 text-base font-bold text-slate-800">
            <span className="text-lg">🚀</span> 지금 할 행동
          </h2>
          <ul className="space-y-2">
            {r.recommended_actions?.map((action, i) => (
              <li key={i} className="flex items-start gap-3 rounded-xl bg-violet-50/70 px-3 py-2">
                <span className="mt-0.5 text-base">{i === 0 ? '❌' : i === 3 ? '📞' : '✅'}</span>
                <span className="text-sm font-medium text-slate-700">{action}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* URL 분석 상세 */}
      {r.url_analyses?.length > 0 && (
        <section className="rounded-2xl border border-violet-100 bg-white px-4 py-5 shadow-sm">
          <h2 className="mb-3 flex items-center gap-2 text-base font-bold text-slate-800">
            <span className="text-lg">🔗</span> URL 분석 상세
          </h2>
          <div className="space-y-2">
            {r.url_analyses.map((ua, i) => (
              <div key={i} className="rounded-xl border border-violet-100 bg-violet-50/70 px-3 py-2">
                <p className="truncate text-xs font-mono text-slate-600">{ua.url}</p>
                <div className="mt-2 flex items-center justify-between">
                  <RiskBadge label={ua.risk_label} />
                  <span className="text-xs font-bold text-slate-500">{Math.round(ua.risk_score)}%</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 신고 문구 */}
      {r.report_template && (
        <section className="rounded-2xl border border-violet-100 bg-white px-4 py-5 shadow-sm">
          <h2 className="mb-3 flex items-center gap-2 text-base font-bold text-slate-800">
            <span className="text-lg">📝</span> 신고 문구
          </h2>
          <div className="relative">
            <pre className="whitespace-pre-wrap break-words rounded-xl bg-violet-950 p-4 text-xs leading-relaxed text-violet-100">
              {r.report_template}
            </pre>
            <button
              onClick={() => navigator.clipboard?.writeText(r.report_template)}
              className="absolute right-3 top-3 rounded-lg bg-white/10 px-3 py-1.5 text-[11px] font-semibold text-white backdrop-blur transition hover:bg-white/20"
            >
              📋 복사
            </button>
          </div>
          {r.report_procedure && (
            <p className="mt-3 text-xs text-slate-500">
              <strong>신고 절차:</strong> {r.report_procedure}
            </p>
          )}
        </section>
      )}

      {/* 보호자 공유 요약 */}
      {r.guardian_summary && (
        <section className="rounded-2xl border-2 border-violet-200 bg-violet-50 px-4 py-5">
          <h2 className="mb-2 flex items-center gap-2 text-base font-bold text-violet-800">
            <span className="text-lg">🛡️</span> 보호자 공유 요약
          </h2>
          <p className="text-sm text-violet-700">{r.guardian_summary}</p>
          <button
            onClick={() => navigator.clipboard?.writeText(r.guardian_summary)}
            className="mt-3 rounded-xl bg-violet-600 px-4 py-2 text-xs font-semibold text-white transition hover:bg-violet-700"
          >
            📋 요약 복사하여 공유
          </button>
        </section>
      )}

      {/* FAQ */}
      {r.faq?.length > 0 && (
        <section className="rounded-2xl border border-violet-100 bg-white px-4 py-5 shadow-sm">
          <h2 className="mb-3 flex items-center gap-2 text-base font-bold text-slate-800">
            <span className="text-lg">❓</span> 자주 묻는 질문
          </h2>
          <div className="space-y-2">
            {r.faq.map((f, i) => (
              <div key={i} className="rounded-xl bg-violet-50/70 px-3 py-2">
                <p className="text-sm font-bold text-slate-800">Q. {f.q}</p>
                <p className="mt-1 text-sm text-slate-600">A. {f.a}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 하단 버튼 */}
      <div className="flex flex-col gap-3 pt-2">
        <button
          onClick={() => navigate('/')}
          className="rounded-2xl border-2 border-violet-200 px-6 py-3 text-sm font-semibold text-slate-700 transition hover:border-violet-300 hover:bg-violet-50"
        >
          🔍 새로운 분석
        </button>
        <button
          onClick={() => navigate('/coaching', { state: { result: r } })}
          className="rounded-2xl bg-gradient-to-r from-violet-600 to-purple-600 px-6 py-3 text-sm font-semibold text-white shadow-lg transition hover:shadow-xl"
        >
          📋 이후 대처 코칭 보기
        </button>
      </div>
    </div>
  )
}

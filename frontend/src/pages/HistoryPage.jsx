export default function HistoryPage() {
  const items = [
    { id: 1, title: '택배 문자', status: '안전', detail: 'url 안전 12%' },
    { id: 2, title: '카드사 안내', status: '위험', detail: 'url 위험 86%' },
    { id: 3, title: '지인 사칭', status: '위험', detail: 'url 위험 74%' },
    { id: 4, title: '정부기관 안내', status: '안전', detail: 'url 안전 22%' },
  ]

  const badgeClass = (status) =>
    status === '위험'
      ? 'bg-rose-100 text-rose-700 border-rose-200'
      : 'bg-emerald-100 text-emerald-700 border-emerald-200'

  return (
    <div className="space-y-6">
      <header className="rounded-2xl border border-violet-100 bg-white p-5 shadow-sm">
        <h1 className="text-xl font-bold text-slate-800">기록</h1>
        <p className="mt-1 text-sm text-slate-500">내가 올렸던 분석 기록을 모아봅니다.</p>
      </header>

      <section className="space-y-3">
        {items.map((item) => (
          <div
            key={item.id}
            className="rounded-2xl border border-violet-100 bg-white px-4 py-4 shadow-sm"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-700">{item.title}</p>
                <p className="text-xs text-slate-400">{item.detail}</p>
              </div>
              <span className={`rounded-full border px-3 py-1 text-xs font-bold ${badgeClass(item.status)}`}>
                {item.status}
              </span>
            </div>
          </div>
        ))}
      </section>
    </div>
  )
}

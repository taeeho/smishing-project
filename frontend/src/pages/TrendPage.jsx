export default function TrendPage() {
  const ageGroups = ['10대', '20대', '30대', '40대', '미공개']
  const top10 = [
    { rank: 1, title: '택배사칭 링크 클릭 유도' },
    { rank: 2, title: '정부기관 사칭 서류 제출' },
    { rank: 3, title: '카드사 보안점검 안내' },
    { rank: 4, title: '저금리 대출/한도 증액' },
    { rank: 5, title: '지인사칭 송금 요청' },
    { rank: 6, title: '계정 로그인 위장 피싱' },
    { rank: 7, title: '모바일 상품권 구매 유도' },
    { rank: 8, title: '환급/지원금 신청 사칭' },
    { rank: 9, title: '택배 재배송/주소 오류' },
    { rank: 10, title: '대리결제/결제 오류 통보' },
  ]

  return (
    <div className="space-y-6">
      <header className="rounded-2xl border border-violet-100 bg-white p-5 shadow-sm">
        <h1 className="text-xl font-bold text-slate-800">트렌드</h1>
        <p className="mt-1 text-sm text-slate-500">
          현재 사용자들이 자주 겪는 유사 사기 유형을 모아 보여줍니다.
        </p>
      </header>

      <section className="rounded-2xl border border-violet-100 bg-white p-5 shadow-sm">
        <h2 className="text-sm font-semibold text-slate-600">나이대 선택</h2>
        <div className="mt-3 grid grid-cols-3 gap-2">
          {ageGroups.map((age) => (
            <button
              key={age}
              type="button"
              className="rounded-xl border border-violet-100 bg-violet-50 px-3 py-2 text-xs font-semibold text-slate-600"
            >
              {age}
            </button>
          ))}
        </div>
      </section>

      <section className="rounded-2xl border border-violet-100 bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-600">최근 가장 많이 당한 스미싱 TOP 10</h2>
          <span className="text-xs text-slate-400">업데이트: 실시간</span>
        </div>
        <div className="mt-4 space-y-3">
          {top10.map((item) => (
            <div
              key={item.rank}
              className="flex items-center justify-between rounded-xl border border-violet-100 bg-violet-50/60 px-4 py-3"
            >
              <div className="flex items-center gap-3">
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-white text-xs font-bold text-violet-600">
                  {item.rank}
                </span>
                <span className="text-sm font-semibold text-slate-700">{item.title}</span>
              </div>
              <span className="text-xs text-slate-400">유사도 ↑</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

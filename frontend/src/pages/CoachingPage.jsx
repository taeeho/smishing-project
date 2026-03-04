import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

const DEFAULT_STEPS = [
  {
    icon: '🔍',
    title: '1단계: 추가 피해 여부 확인',
    desc: '링크를 클릭했거나, 앱을 설치했거나, 개인정보를 입력한 적이 있는지 확인하세요.',
    checklist: [
      '의심 링크를 클릭한 적이 있나요?',
      '알 수 없는 앱을 설치했나요?',
      '개인정보(이름, 주민번호 등)를 입력했나요?',
      '돈을 보낸 적이 있나요?',
    ],
  },
  {
    icon: '🏦',
    title: '2단계: 금융 앱 / 계좌 점검',
    desc: '은행 앱에서 비정상 거래가 없는지 확인하세요.',
    checklist: [
      '최근 거래 내역에 이상이 없는지 확인',
      '모르는 출금/이체가 없는지 확인',
      '카드 결제 알림에 이상한 내역이 없는지 확인',
      '필요 시 은행에 지급정지 요청',
    ],
  },
  {
    icon: '👨‍👩‍👧‍👦',
    title: '3단계: 보호자 / 가족 공유',
    desc: '이 상황을 가족이나 보호자에게 알려주세요.',
    checklist: [
      '보호자에게 상황 공유',
      '같은 문자를 받은 가족이 있는지 확인',
      '가족 모두 의심 링크 차단',
    ],
  },
  {
    icon: '📞',
    title: '4단계: 기관 신고',
    desc: '필요한 경우 관련 기관에 신고하세요.',
    checklist:[
      '경찰청 112 신고',
      '금융감독원 1332 피해구제 신청',
      'KISA 118 스팸 신고',
      '의심 번호 차단 및 스팸 등록',
    ],
  },
  {
    icon: '🔒',
    title: '5단계: 후속 보안 조치',
    desc: '재발 방지를 위한 보안 조치를 취하세요.',
    checklist: [
      '비밀번호 변경 (특히 금융 서비스)',
      '2단계 인증(OTP) 활성화',
      '스마트폰 악성앱 검사 실행',
      '모르는 앱 삭제',
    ],
  },
]

export default function CoachingPage() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const result = state?.result
  const [checked, setChecked] = useState({})

  const steps = result?.coaching_steps
    ? result.coaching_steps.map((step, i) => ({
        icon: DEFAULT_STEPS[i]?.icon || '📋',
        title: step.split(':')[0] || step,
        desc: step.split(':').slice(1).join(':').trim() || '',
        checklist: DEFAULT_STEPS[i]?.checklist || [],
      }))
    : DEFAULT_STEPS

  const toggle = (stepIdx, checkIdx) => {
    const key = `${stepIdx}-${checkIdx}`
    setChecked((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  const totalItems = steps.reduce((sum, s) => sum + s.checklist.length, 0)
  const completedItems = Object.values(checked).filter(Boolean).length
  const progress = totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0

  return (
    <div className="space-y-8">
      {/* 헤더 */}
      <header className="text-center">
        <div className="mb-4 inline-flex h-20 w-20 items-center justify-center rounded-3xl bg-gradient-to-br from-violet-400 to-purple-600 text-4xl shadow-xl shadow-violet-200">
          📋
        </div>
        <h1 className="text-3xl font-bold">이후 대처 코칭</h1>
        <p className="mt-2 text-lg text-slate-500">
          단계별로 따라하면서 안전을 확인하세요
        </p>
      </header>

      {/* 진행률 */}
      <div className="rounded-2xl border border-violet-100 bg-white p-6 shadow-md">
        <div className="flex items-center justify-between">
          <span className="font-bold text-slate-700">진행률</span>
          <span className="text-2xl font-bold text-violet-600">{progress}%</span>
        </div>
        <div className="mt-3 h-4 overflow-hidden rounded-full bg-violet-100">
          <div
            className="h-full rounded-full bg-gradient-to-r from-violet-400 to-purple-500 transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="mt-2 text-sm text-slate-500">
          {completedItems}/{totalItems} 항목 완료
        </p>
      </div>

      {/* 코칭 */}
      <div className="space-y-4">
        {steps.map((step, si) =>{
          const stepChecked = step.checklist.filter((_, ci) => checked[`${si}-${ci}`]).length
          const stepDone = stepChecked === step.checklist.length && step.checklist.length > 0

          return (
            <div
              key={si}
              className={`rounded-2xl border p-6 transition-all ${
                stepDone
                  ? 'border-violet-200 bg-violet-50'
                  : 'border-violet-100 bg-white shadow-md'
            }`}
          >
              <div className="flex items-center gap-3">
                <span className="text-3xl">{step.icon}</span>
                <div>
                  <h3 className="text-lg font-bold text-slate-800">
                    {step.title}
                    {stepDone && <span className="ml-2 text-violet-500">✓ 완료</span>}
                  </h3>
                  {step.desc && <p className="text-sm text-slate-500">{step.desc}</p>}
                </div>
              </div>

              {step.checklist.length > 0 && (
                <ul className="mt-4 space-y-2 pl-2">
                  {step.checklist.map((item, ci) => {
                    const key = `${si}-${ci}`
                    return (
                      <li key={ci}>
                        <label className="flex cursor-pointer items-center gap-3 rounded-xl px-3 py-2 transition hover:bg-violet-50">
                          <input
                            type="checkbox"
                            checked={!!checked[key]}
                            onChange={() => toggle(si, ci)}
                            className="h-5 w-5 rounded border-violet-300 text-violet-600 focus:ring-violet-500"
                          />
                          <span className={`text-sm ${checked[key] ? 'text-slate-400 line-through' : 'text-slate-700'}`}>
                            {item}
                          </span>
                        </label>
                      </li>
                    )
                  })}
                </ul>
              )}
            </div>
          )
        })}
      </div>

      {/* 긴급 연락처 */}
      <div className="rounded-2xl border border-violet-200 bg-violet-50 p-6">
        <h2 className="mb-4 text-xl font-bold text-violet-800">📞 긴급 연락처</h2>
        <div className="grid gap-3 sm:grid-cols-3">
          {[
            { name: '경찰청', number: '112', desc: '피해 신고 및 수사 의뢰' },
            { name: '금융감독원', number: '1332', desc: '금융 피해 구제 신청' },
            { name: 'KISA', number: '118', desc: '스팸/피싱 신고' },
          ].map((contact) => (
            <div key={contact.number} className="rounded-xl bg-white p-4 text-center shadow-sm">
              <p className="text-2xl font-bold text-violet-600">{contact.number}</p>
              <p className="font-semibold text-slate-800">{contact.name}</p>
              <p className="text-xs text-slate-500">{contact.desc}</p>
            </div>
          ))}
        </div>
      </div>
      
{/* 하단버튼 */}
      <div className="flex flex-wrap justify-center gap-4 pt-4">
        <button onClick={() => navigate('/')} className="rounded-2xl border-2 border-violet-200 px-8 py-3 font-semibold text-slate-700 transition hover:border-violet-300 hover:bg-violet-50">🔍 새로운 분석</button>
        <button onClick={() => navigate('/guardian')} className="rounded-2xl bg-gradient-to-r from-violet-600 to-purple-600 px-8 py-3 font-semibold text-white shadow-lg transition hover:shadow-xl">🛡️ 보호자 모드</button>
      </div>
    </div>
  )
}
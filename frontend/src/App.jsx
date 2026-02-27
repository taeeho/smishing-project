import { useMemo, useState } from 'react'
import axios from 'axios'

const initialForm = {
  smishing_type: '',
  url_risk_score: '',
  url_domain: '',
  ner_entities: '',
  group_risk: false,
  masked_text: '',
  input_type: 'text',
}

function App() {
  const [form, setForm] = useState(initialForm)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const payload = useMemo(() => {
    const entities = form.ner_entities
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
    const score =
      form.url_risk_score === '' ? null : Number(form.url_risk_score)
    return {
      smishing_type: form.smishing_type || null,
      url_risk_score: Number.isNaN(score) ? null : score,
      url_domain: form.url_domain || null,
      ner_entities: entities.length ? entities : null,
      group_risk: form.group_risk || null,
      masked_text: form.masked_text || null,
      input_type: form.input_type || null,
    }
  }, [form])

  const onSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const response = await axios.post('/api/coach/', payload)
      setResult(response.data)
    } catch (err) {
      setError('요청 처리 중 오류가 발생했어요. 다시 시도해 주세요.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-white to-sky-50 text-slate-900">
      <div className="mx-auto w-full max-w-5xl px-6 py-10">
        <header className="mb-10 flex flex-col gap-3">
          <p className="text-sm uppercase tracking-[0.2em] text-slate-500">
            Smishing Coach
          </p>
          <h1 className="text-4xl font-semibold leading-tight">
            스미싱 대응 전문 AI 코치
          </h1>
          <p className="text-lg text-slate-600">
            분석 결과를 입력하면, 보호자와 사용자 모두가 바로 이해할 수 있는
            행동 가이드를 만듭니다.
          </p>
        </header>

        <div className="grid gap-8 lg:grid-cols-[1.1fr_1fr]">
          <section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-[0_20px_60px_-40px_rgba(15,23,42,0.5)]">
            <h2 className="mb-6 text-2xl font-semibold">분석 입력</h2>
            <form className="space-y-5" onSubmit={onSubmit}>
              <div>
                <label className="text-sm font-semibold text-slate-600">
                  BERT 분류 결과
                </label>
                <input
                  className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 text-base focus:border-slate-400 focus:outline-none"
                  placeholder="예: 택배 사칭"
                  value={form.smishing_type}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, smishing_type: e.target.value }))
                  }
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="text-sm font-semibold text-slate-600">
                    URL 위험도 점수
                  </label>
                  <input
                    className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 text-base focus:border-slate-400 focus:outline-none"
                    placeholder="0~100"
                    value={form.url_risk_score}
                    onChange={(e) =>
                      setForm((prev) => ({ ...prev, url_risk_score: e.target.value }))
                    }
                  />
                </div>
                <div>
                  <label className="text-sm font-semibold text-slate-600">
                    의심 도메인
                  </label>
                  <input
                    className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 text-base focus:border-slate-400 focus:outline-none"
                    placeholder="예: delivery-check.co"
                    value={form.url_domain}
                    onChange={(e) =>
                      setForm((prev) => ({ ...prev, url_domain: e.target.value }))
                    }
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-semibold text-slate-600">
                  NER 엔티티 (쉼표로 구분)
                </label>
                <input
                  className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 text-base focus:border-slate-400 focus:outline-none"
                  placeholder="예: 택배, 배송비, 인증번호"
                  value={form.ner_entities}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, ner_entities: e.target.value }))
                  }
                />
              </div>

              <div>
                <label className="text-sm font-semibold text-slate-600">
                  메시지 요약 (마스킹)
                </label>
                <textarea
                  className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 text-base focus:border-slate-400 focus:outline-none"
                  rows={3}
                  placeholder="예: 택배 보관료 결제 요청"
                  value={form.masked_text}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, masked_text: e.target.value }))
                  }
                />
              </div>

              <div className="flex flex-wrap items-center gap-4">
                <label className="flex items-center gap-2 text-sm font-semibold text-slate-600">
                  <input
                    type="checkbox"
                    checked={form.group_risk}
                    onChange={(e) =>
                      setForm((prev) => ({ ...prev, group_risk: e.target.checked }))
                    }
                  />
                  집단 위험 신호 있음
                </label>
                <select
                  className="rounded-xl border border-slate-200 px-4 py-2 text-base focus:border-slate-400 focus:outline-none"
                  value={form.input_type}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, input_type: e.target.value }))
                  }
                >
                  <option value="text">text</option>
                  <option value="image">image</option>
                </select>
              </div>

              <button
                type="submit"
                className="w-full rounded-2xl bg-slate-900 px-5 py-3 text-lg font-semibold text-white transition hover:bg-slate-800"
                disabled={loading}
              >
                {loading ? '분석 중...' : '결과 생성'}
              </button>

              {error && <p className="text-sm text-rose-600">{error}</p>}
            </form>
          </section>

          <section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-[0_20px_60px_-40px_rgba(15,23,42,0.5)]">
            <h2 className="mb-6 text-2xl font-semibold">출력 JSON</h2>
            {!result && (
              <div className="rounded-2xl border border-dashed border-slate-200 p-6 text-slate-500">
                결과가 아직 없어요. 왼쪽 입력 후 생성 버튼을 눌러주세요.
              </div>
            )}
            {result && (
              <pre className="whitespace-pre-wrap rounded-2xl bg-slate-900 p-5 text-sm text-emerald-200">
                {JSON.stringify(result, null, 2)}
              </pre>
            )}
          </section>
        </div>
      </div>
    </div>
  )
}

export default App

import { useEffect, useState } from 'react'
import axios from 'axios'

export default function ProfilePage() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [form, setForm] = useState({
    username: '',
    email: '',
    age: '',
    guardian_contact: '',
  })

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError('')
      setSuccess('')
      try {
        const token = localStorage.getItem('access_token')
        if (!token) {
          setError('로그인이 필요합니다.')
          setLoading(false)
          return
        }
        const res = await axios.get('/api/auth/me', {
          headers: { Authorization: `Bearer ${token}` },
        })
        const data = res.data
        setForm({
          username: data.username || '',
          email: data.email || '',
          age: data.age ?? '',
          guardian_contact: data.guardian_contact || '',
        })
      } catch (err) {
        setError('회원정보를 불러오지 못했습니다.')
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [])

  const onChange = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const formatPhone = (value) => {
    const digits = value.replace(/\D/g, '').slice(0, 11)
    if (digits.length <= 3) return digits
    if (digits.length <= 7) return `${digits.slice(0, 3)}-${digits.slice(3)}`
    return `${digits.slice(0, 3)}-${digits.slice(3, 7)}-${digits.slice(7)}`
  }

  const onSave = async () => {
    setSaving(true)
    setError('')
    setSuccess('')
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setError('로그인이 필요합니다.')
        setSaving(false)
        return
      }
      const payload = {
        username: form.username,
        age: form.age === '' ? null : Number(form.age),
        guardian_contact: form.guardian_contact,
      }
      const res = await axios.patch('/api/auth/me', payload, {
        headers: { Authorization: `Bearer ${token}` },
      })
      const data = res.data
      localStorage.setItem('auth_user', JSON.stringify({
        user_id: data.user_id,
        email: data.email,
        username: data.username,
        social_type: data.social_type,
      }))
      setSuccess('회원정보가 저장되었습니다.')
    } catch (err) {
      setError('저장에 실패했습니다. 다시 시도해주세요.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-violet-200 border-t-violet-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <header className="rounded-2xl border border-violet-100 bg-white p-5 shadow-sm">
        <h1 className="text-xl font-bold text-slate-800">회원정보</h1>
        <p className="mt-1 text-sm text-slate-500">현재 로그인된 회원 정보를 확인하고 수정할 수 있어요.</p>
      </header>

      {error && (
        <div className="rounded-xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-600">
          {error}
        </div>
      )}
      {success && (
        <div className="rounded-xl bg-violet-50 px-4 py-3 text-sm font-medium text-violet-700">
          {success}
        </div>
      )}

      <section className="rounded-2xl border border-violet-100 bg-white p-5 shadow-sm">
        <div className="space-y-4">
          <div>
            <label className="text-sm font-semibold text-slate-600">이메일</label>
            <input value={form.email} disabled className="mt-2 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500" />
          </div>
          <div>
            <label className="text-sm font-semibold text-slate-600">이름</label>
            <input value={form.username} onChange={(e) => onChange('username', e.target.value)} className="mt-2 w-full rounded-xl border border-violet-200 bg-white px-4 py-3 text-sm text-slate-700 focus:border-violet-400 focus:outline-none focus:ring-2 focus:ring-violet-200" />
          </div>
          <div>
            <label className="text-sm font-semibold text-slate-600">나이</label>
            <input type="number" min="0" value={form.age} onChange={(e) => onChange('age', e.target.value)} className="mt-2 w-full rounded-xl border border-violet-200 bg-white px-4 py-3 text-sm text-slate-700 focus:border-violet-400 focus:outline-none focus:ring-2 focus:ring-violet-200" />
          </div>
          <div>
            <label className="text-sm font-semibold text-slate-600">보호자 연락처</label>
            <input value={form.guardian_contact} inputMode="numeric" placeholder="010-0000-0000"
              className="mt-2 w-full rounded-xl border border-violet-200 bg-white px-4 py-3 text-sm text-slate-700 focus:border-violet-400 focus:outline-none focus:ring-2 focus:ring-violet-200"
              onChange={(e) => onChange('guardian_contact', formatPhone(e.target.value))}
            />
          </div>
        </div>

        <button type="button" onClick={onSave} disabled={saving} className="mt-5 w-full rounded-2xl bg-violet-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-60">{saving ? '저장 중...' : '회원정보 저장'}</button>
      </section>
    </div>
  )
}

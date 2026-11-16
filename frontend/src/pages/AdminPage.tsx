import { CheckCircle2, RotateCcw, ShieldAlert, UserX } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { AppCard } from '../components/common/AppCard'
import { PageHeader } from '../components/common/PageHeader'
import { useAuth } from '../hooks/useAuth'
import { apiErrorMessage, changeUserStatus, getAdminSummary, listAdminUsers, type AccountStatus, type AdminSummary, type AdminUser } from '../services/api'

type Filter = AccountStatus | 'all'
const filters: Array<{ value: Filter; label: string }> = [{ value: 'pending', label: 'Pending approval' }, { value: 'approved', label: 'Approved' }, { value: 'inactive', label: 'Deactivated' }, { value: 'all', label: 'All users' }]
const statusStyle: Record<AccountStatus, string> = { pending: 'bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-100', approved: 'bg-emerald-100 text-emerald-900 dark:bg-emerald-950 dark:text-emerald-100', inactive: 'bg-slate-200 text-slate-800 dark:bg-slate-800 dark:text-slate-100' }
const statusLabel: Record<AccountStatus, string> = { pending: 'Pending', approved: 'Approved', inactive: 'Deactivated' }
const when = (value: string | null) => value ? new Date(value).toLocaleString() : 'Never'

export function AdminPage() {
  const { user } = useAuth()
  const [filter, setFilter] = useState<Filter>('pending')
  const [users, setUsers] = useState<AdminUser[]>([])
  const [summary, setSummary] = useState<AdminSummary>()
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState<number | null>(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const isAdmin = user?.role === 'admin'

  const load = useCallback(async (status: Filter) => {
    setLoading(true); setError('')
    try { const [counts, list] = await Promise.all([getAdminSummary(), listAdminUsers(status)]); setSummary(counts); setUsers(list) }
    catch (reason) { setError(apiErrorMessage(reason, 'Users could not be loaded.')) }
    finally { setLoading(false) }
  }, [])
  useEffect(() => { if (isAdmin) void load(filter) }, [isAdmin, filter, load])

  async function act(target: AdminUser, action: 'approve' | 'deactivate' | 'reactivate') {
    if (action === 'deactivate' && !window.confirm(`Deactivate ${target.full_name}? They will be signed out everywhere until reactivated.`)) return
    setBusy(target.id); setMessage(''); setError('')
    try {
      const updated = await changeUserStatus(target.id, action)
      setMessage(`${updated.full_name} is now ${statusLabel[updated.status].toLowerCase()}.`)
      await load(filter)
    } catch (reason) { setError(apiErrorMessage(reason, 'The account could not be updated.')) }
    finally { setBusy(null) }
  }

  if (!isAdmin) return <AppCard className="mx-auto max-w-xl p-8 text-center"><ShieldAlert className="mx-auto size-10 text-[var(--muted)]" aria-hidden="true" /><h1 className="mt-4 text-2xl font-bold">Administrator access required</h1><p className="mt-2 text-[var(--muted)]">This page is available only to administrators.</p></AppCard>

  return <div className="space-y-6">
    <PageHeader title="User administration" description="Approve new registrations and manage account access. Self-registered users cannot sign in until an administrator approves them." />
    <div className="flex flex-wrap gap-2" role="group" aria-label="Filter users by status">
      {filters.map(item => <button key={item.value} type="button" aria-pressed={filter === item.value} onClick={() => { setMessage(''); setFilter(item.value) }} className={`min-h-11 rounded-xl border border-[var(--border)] px-4 font-semibold ${filter === item.value ? 'bg-[var(--primary-strong)] text-white' : 'bg-[var(--surface)]'}`}>{item.label}{summary ? ` (${summary[item.value]})` : ''}</button>)}
    </div>
    {message && <p role="status" className="rounded-xl bg-emerald-50 p-3 text-emerald-900 dark:bg-emerald-950 dark:text-emerald-100">{message}</p>}
    {error && <p role="alert" className="rounded-xl bg-rose-50 p-3 text-rose-800 dark:bg-rose-950 dark:text-rose-100">{error}</p>}
    {loading ? <p role="status" className="text-[var(--muted)]">Loading users…</p> : users.length === 0 ? <AppCard className="p-6 text-[var(--muted)]">{filter === 'pending' ? 'No registrations are waiting for approval.' : 'No users match this filter.'}</AppCard> :
      <ul className="space-y-3" aria-label="Users">{users.map(item => <li key={item.id}><AppCard className="flex flex-col gap-4 p-5 lg:flex-row lg:items-center lg:justify-between">
        <div className="min-w-0 space-y-1">
          <div className="flex flex-wrap items-center gap-2"><strong className="text-lg">{item.full_name}</strong><span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${statusStyle[item.status]}`}>{statusLabel[item.status]}</span>{item.role === 'admin' && <span className="rounded-full bg-[var(--primary-soft)] px-2.5 py-0.5 text-xs font-semibold text-[var(--primary-strong)]">Administrator</span>}{item.id === user?.id && <span className="text-xs text-[var(--muted)]">(you)</span>}</div>
          <p className="break-all text-[var(--muted)]">{item.email}</p>
          <p className="text-sm text-[var(--muted)]">Registered {when(item.created_at)} · Last sign-in {when(item.last_login_at)} · {item.profile_count} {item.profile_count === 1 ? 'profile' : 'profiles'} · Email {item.email_verified ? 'verified' : 'not verified'}{item.deletion_requested_at ? ' · Deletion requested' : ''}</p>
        </div>
        <div className="flex shrink-0 flex-wrap gap-2">
          {item.status === 'pending' && <button type="button" aria-label={`Approve ${item.full_name}`} disabled={busy === item.id} onClick={() => void act(item, 'approve')} className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-[var(--primary-strong)] px-4 font-semibold text-white disabled:opacity-60"><CheckCircle2 className="size-4" aria-hidden="true" />Approve</button>}
          {item.status !== 'inactive' && item.role !== 'admin' && <button type="button" aria-label={`Deactivate ${item.full_name}`} disabled={busy === item.id} onClick={() => void act(item, 'deactivate')} className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-[var(--border)] px-4 font-semibold disabled:opacity-60"><UserX className="size-4" aria-hidden="true" />Deactivate</button>}
          {item.status === 'inactive' && <button type="button" aria-label={`Reactivate ${item.full_name}`} disabled={busy === item.id} onClick={() => void act(item, 'reactivate')} className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-[var(--border)] px-4 font-semibold disabled:opacity-60"><RotateCcw className="size-4" aria-hidden="true" />Reactivate</button>}
        </div>
      </AppCard></li>)}</ul>}
  </div>
}

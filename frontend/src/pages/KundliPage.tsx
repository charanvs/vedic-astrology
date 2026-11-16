import { CheckCircle2, Info } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { AppCard } from '../components/common/AppCard'
import { PageHeader } from '../components/common/PageHeader'
import { KundliWorkspace } from '../components/kundli/KundliWorkspace'
import { BirthProfileForm } from '../components/profiles/BirthProfileForm'
import { apiErrorMessage, getBirthProfile, getBirthProfiles } from '../services/api'
import type { BirthProfile } from '../types/api'

export function KundliPage() {
  const { id } = useParams()
  const [profiles, setProfiles] = useState<BirthProfile[]>([])
  const [profile, setProfile] = useState<BirthProfile>()
  const [selectedProfile, setSelectedProfile] = useState<BirthProfile>()
  const [savedProfile, setSavedProfile] = useState<BirthProfile>()
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const editing = Boolean(id)

  useEffect(() => {
    setLoading(true); setError('')
    Promise.all([getBirthProfiles(100), id ? getBirthProfile(Number(id)) : Promise.resolve(undefined)])
      .then(([items, edited]) => { setProfiles(items); if (edited) setProfile(edited); setSelectedProfile(edited ?? items[0]) })
      .catch((reason) => setError(apiErrorMessage(reason, 'Birth profiles could not be loaded.')))
      .finally(() => setLoading(false))
  }, [id])

  const handleSaved = (saved: BirthProfile) => {
    if (editing) setProfile(saved)
    setSavedProfile(saved); setSelectedProfile(saved)
    setProfiles((current) => [saved, ...current.filter((item) => item.id !== saved.id)])
  }

  return <div className="mx-auto max-w-7xl space-y-6">
    <PageHeader title="North Indian Janam Kundli" description="Create or select a birth profile to generate a fixed-house diamond chart from Swiss Ephemeris data." />
    {savedProfile && <div role="status" className="flex flex-wrap items-center gap-3 rounded-2xl border border-emerald-300 bg-emerald-50 p-4 text-emerald-900 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-100"><CheckCircle2 className="size-5 shrink-0" aria-hidden="true"/><div className="min-w-0 flex-1"><strong>{editing ? 'Profile updated in the database.' : 'Profile saved to the database.'}</strong><p className="text-sm">{savedProfile.full_name} is now selected and available throughout the application.</p></div><Link to={`/birth-profiles/${savedProfile.id}`} className="rounded-xl border border-emerald-400 px-3 py-2 text-sm font-bold">View saved profile</Link><Link to="/saved-charts" className="rounded-xl bg-emerald-700 px-3 py-2 text-sm font-bold text-white">All saved profiles</Link></div>}
    <div className="flex gap-3 rounded-2xl border border-[var(--border)] bg-[var(--primary-soft)] p-4 text-sm text-[var(--primary-strong)]"><Info className="mt-0.5 size-5 shrink-0" aria-hidden="true" /><p><strong>Privacy notice:</strong> Do not enter sensitive personal data. Authentication and production data safeguards belong to a later milestone.</p></div>
    {error && <p role="alert" className="rounded-xl bg-rose-50 p-4 text-rose-800 dark:bg-rose-950 dark:text-rose-200">{error}</p>}
    <AppCard className="p-5">
      <label className="text-sm font-bold" htmlFor="kundli-profile-selection">Saved birth profile</label>
      <select id="kundli-profile-selection" value={selectedProfile?.id ?? ''} onChange={(event) => setSelectedProfile(profiles.find((item) => item.id === Number(event.target.value)))} className="mt-2 min-h-11 w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3"><option value="">Select a saved profile</option>{profiles.map((item) => <option key={item.id} value={item.id}>{item.full_name} · {item.birth_date} · {item.location.city}</option>)}</select>
      {!loading && profiles.length === 0 && <p className="mt-3 text-sm text-[var(--muted)]">No saved profiles yet. Complete the birth profile form below.</p>}
    </AppCard>
    {selectedProfile && <KundliWorkspace profile={selectedProfile} />}
    <details open={editing || profiles.length === 0} className="group rounded-2xl border border-[var(--border)] bg-[var(--surface)] shadow-sm">
      <summary className="cursor-pointer list-none px-5 py-4 text-lg font-bold">{editing ? 'Edit birth profile' : 'Create a new birth profile'}<span className="float-right text-sm font-normal text-[var(--muted)] group-open:hidden">Open form</span></summary>
      <div className="border-t border-[var(--border)] p-5 sm:p-7">{loading && editing && !profile ? <p role="status" className="text-[var(--muted)]">Loading profile…</p> : <BirthProfileForm profile={profile} onSaved={handleSaved} />}</div>
    </details>
  </div>
}

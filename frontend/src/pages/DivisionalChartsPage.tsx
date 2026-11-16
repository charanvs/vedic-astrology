import { AlertTriangle, Layers3 } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { AppCard } from '../components/common/AppCard'
import { PageHeader } from '../components/common/PageHeader'
import { DivisionalChartPanel } from '../components/divisional/DivisionalChartPanel'
import { DivisionalPlanetTable } from '../components/divisional/DivisionalPlanetTable'
import { apiErrorMessage, calculateBirthProfile, getBirthProfiles, getDivisionalProfile } from '../services/api'
import type { AstrologyCalculation, BirthProfile, DivisionalChart, DivisionalChartType } from '../types/api'

type Tab = 'D1' | DivisionalChartType

export function DivisionalChartsPage() {
  const [profiles, setProfiles] = useState<BirthProfile[]>([]), [profileId, setProfileId] = useState<number | null>(null)
  const [tab, setTab] = useState<Tab>('D9'), [d1, setD1] = useState<AstrologyCalculation>(), [d9, setD9] = useState<DivisionalChart>(), [d10, setD10] = useState<DivisionalChart>()
  const [loading, setLoading] = useState(true), [error, setError] = useState('')
  useEffect(() => { getBirthProfiles(100).then(items => { setProfiles(items); const exact = items.find(item => !item.birth_time_unknown && item.birth_time_utc); if (exact) setProfileId(exact.id) }).catch(reason => setError(apiErrorMessage(reason, 'Saved profiles could not be loaded.'))).finally(() => setLoading(false)) }, [])
  useEffect(() => {
    if (!profileId) return
    const controller = new AbortController()
    // A profile change intentionally resets all three chart requests.
    // oxlint-disable-next-line react/set-state-in-effect
    setLoading(true); setError(''); setD1(undefined); setD9(undefined); setD10(undefined)
    Promise.all([calculateBirthProfile(profileId), getDivisionalProfile(profileId, 'D9', controller.signal), getDivisionalProfile(profileId, 'D10', controller.signal)])
      .then(([birth, navamsha, dashamsha]) => { setD1(birth); setD9(navamsha); setD10(dashamsha) })
      .catch(reason => { const message = apiErrorMessage(reason, 'Divisional charts could not be calculated.'); if (message) setError(message) })
      .finally(() => setLoading(false))
    return () => controller.abort()
  }, [profileId])
  const profile = useMemo(() => profiles.find(item => item.id === profileId), [profiles, profileId])
  const selected = tab === 'D9' ? d9 : tab === 'D10' ? d10 : d1
  const warnings = selected?.warnings ?? []
  return <div className="min-w-0 space-y-6">
    <PageHeader title="Divisional Charts" description="Navamsha (D9) and Dashamsha (D10) · Parashari calculation from exact D1 sidereal longitudes"/>
    <AppCard className="p-5"><label className="block max-w-xl text-sm font-bold" htmlFor="division-profile">Birth profile</label><select id="division-profile" value={profileId ?? ''} onChange={event => setProfileId(Number(event.target.value) || null)} className="mt-2 min-h-11 w-full max-w-xl rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3"><option value="">Select an exact-time profile</option>{profiles.map(item => <option key={item.id} value={item.id} disabled={item.birth_time_unknown || !item.birth_time_utc}>{item.full_name} · {item.birth_date}{item.birth_time_unknown ? ' · exact time required' : ''}</option>)}</select></AppCard>
    <div role="tablist" aria-label="Chart division" className="flex flex-wrap gap-2">{(['D1','D9','D10'] as Tab[]).map(item => <button key={item} role="tab" aria-selected={tab === item} onClick={() => setTab(item)} className={`min-h-11 rounded-xl px-5 font-bold ${tab === item ? 'bg-[var(--primary-strong)] text-white' : 'border border-[var(--border)] bg-[var(--surface)]'}`}>{item}{item === 'D9' ? ' Navamsha' : item === 'D10' ? ' Dashamsha' : ' Rashi'}</button>)}</div>
    {loading ? <p role="status" className="text-[var(--muted)]">Calculating D1, D9, and D10 charts…</p> : error ? <p role="alert" className="rounded-2xl bg-rose-50 p-5 text-rose-800 dark:bg-rose-950 dark:text-rose-200">{error}</p> : !profile ? <AppCard className="p-8 text-center"><Layers3 className="mx-auto size-10 text-[var(--muted)]"/><p className="mt-3 font-semibold">Create or select a saved profile with an exact birth time.</p></AppCard> : d1 && selected ? <>
      {warnings.length > 0 && <div className="flex gap-3 rounded-2xl bg-amber-50 p-4 text-sm text-amber-900 dark:bg-amber-950 dark:text-amber-100"><AlertTriangle className="size-5 shrink-0"/><div><strong>Calculation notes</strong><ul className="mt-1 list-disc pl-5">{warnings.map(warning => <li key={warning}>{warning}</li>)}</ul></div></div>}
      <AppCard className="p-4 sm:p-6">{tab === 'D1' ? <DivisionalChartPanel chart={d1} profile={profile}/> : <><div className="grid items-start gap-8 2xl:grid-cols-2"><DivisionalChartPanel chart={d1} profile={profile} compact/><DivisionalChartPanel chart={selected} profile={profile} compact/></div><div className="mt-8"><DivisionalPlanetTable chart={selected}/></div></>}</AppCard>
      <p className="text-sm text-[var(--muted)]">Divisional charts use Lahiri sidereal longitudes and the mean lunar node from the D1 calculation. They provide calculated positions only, not predictive interpretation.</p>
    </> : null}
  </div>
}

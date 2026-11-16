import { AlertTriangle, Moon, Orbit } from 'lucide-react'
import { useEffect, useState } from 'react'
import { AppCard } from '../common/AppCard'
import { apiErrorMessage, calculateBirthProfile } from '../../services/api'
import type { AstrologyCalculation, BirthProfile } from '../../types/api'

export function CalculationSummary({profile}:{profile:BirthProfile}){
 const [result,setResult]=useState<AstrologyCalculation>(),[error,setError]=useState(''),[loading,setLoading]=useState(false)
 useEffect(()=>{if(profile.birth_time_unknown){setResult(undefined);setError('');return}setLoading(true);setError('');calculateBirthProfile(profile.id).then(setResult).catch(reason=>setError(apiErrorMessage(reason,'Astronomical calculation could not be completed.'))).finally(()=>setLoading(false))},[profile])
 if(profile.birth_time_unknown)return <AppCard className="p-5"><div className="flex gap-3 text-amber-800 dark:text-amber-200"><AlertTriangle className="size-5 shrink-0"/><p><strong>Exact birth time required.</strong> Lagna and houses are not calculated for an unknown time.</p></div></AppCard>
 if(loading)return <p role="status" className="text-[var(--muted)]">Calculating astronomical positions…</p>
 if(error)return <p role="alert" className="rounded-xl bg-rose-50 p-4 text-rose-800 dark:bg-rose-950 dark:text-rose-200">{error}</p>
 if(!result)return null
 const moon=result.planets.find(item=>item.identifier==='moon')
 return <AppCard className="p-5 sm:p-6"><h2 className="flex items-center gap-2 text-xl font-bold"><Orbit className="size-5 text-[var(--primary-strong)]"/>Calculation summary</h2><p className="mt-1 text-sm text-[var(--muted)]">Astronomical calculations based on Swiss Ephemeris.</p><dl className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3"><div><dt className="text-sm text-[var(--muted)]">Lagna</dt><dd className="font-bold">{result.lagna.rashi.name} · {result.lagna.longitude_formatted}</dd></div><div><dt className="text-sm text-[var(--muted)]">Moon Rashi</dt><dd className="font-bold">{moon?.rashi.name}</dd></div><div><dt className="text-sm text-[var(--muted)]">Moon Nakshatra</dt><dd className="flex items-center gap-1 font-bold"><Moon className="size-4"/>{moon?.nakshatra.name} · Pada {moon?.nakshatra.pada}</dd></div><div><dt className="text-sm text-[var(--muted)]">Lahiri ayanamsa</dt><dd className="font-semibold">{result.ayanamsa.formatted}</dd></div><div><dt className="text-sm text-[var(--muted)]">Engine source</dt><dd className="font-semibold">{result.engine.ephemeris_source}</dd></div><div><dt className="text-sm text-[var(--muted)]">UTC</dt><dd className="font-semibold">{result.birth_datetime.utc_datetime}</dd></div></dl></AppCard>
}

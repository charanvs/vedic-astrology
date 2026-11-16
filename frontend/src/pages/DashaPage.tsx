import { useEffect, useState } from 'react'
import { AppCard } from '../components/common/AppCard'
import { PageHeader } from '../components/common/PageHeader'
import { DashaDashboard } from '../components/dasha/DashaDashboard'
import { DashaError } from '../components/dasha/DashaError'
import { DashaLoading } from '../components/dasha/DashaLoading'
import { DashaProfileSelector } from '../components/dasha/DashaProfileSelector'
import { DashaSettings } from '../components/dasha/DashaSettings'
import { utcInputToIso } from '../components/dasha/dashaFormat'
import { apiErrorMessage, getBirthProfiles, getDashaProfile } from '../services/api'
import type { BirthProfile, DashaResult, DashaYearConvention } from '../types/api'

export function DashaPage(){
 const [profiles,setProfiles]=useState<BirthProfile[]>([]),[profileId,setProfileId]=useState<number|null>(null)
 const [convention,setConvention]=useState<DashaYearConvention>(()=>(localStorage.getItem('dasha-year-convention') as DashaYearConvention)||'365.25_day'),[reference,setReference]=useState('')
 const [result,setResult]=useState<DashaResult>(),[loadingProfiles,setLoadingProfiles]=useState(true),[loading,setLoading]=useState(false),[error,setError]=useState(''),[retry,setRetry]=useState(0)
 useEffect(()=>{getBirthProfiles(100).then(items=>{setProfiles(items);const exact=items.find(item=>!item.birth_time_unknown&&item.birth_time_utc);if(exact)setProfileId(exact.id)}).catch(reason=>setError(apiErrorMessage(reason,'Saved profiles could not be loaded.'))).finally(()=>setLoadingProfiles(false))},[])
 useEffect(()=>{if(!profileId)return;const controller=new AbortController();
  // A new external calculation intentionally resets request state.
  // oxlint-disable-next-line react/set-state-in-effect
  setLoading(true);setError('');getDashaProfile(profileId,convention,utcInputToIso(reference),controller.signal).then(setResult).catch(reason=>{const message=apiErrorMessage(reason,'Dasha calculation could not be completed.');if(message)setError(message)}).finally(()=>setLoading(false));return()=>controller.abort()},[profileId,convention,reference,retry])
 return <div className="min-w-0 space-y-6"><PageHeader title="Vimshottari Dasha" description="Traditional Planetary Periods and Timeline"/><AppCard className="grid min-w-0 gap-5 p-5 lg:grid-cols-2"><DashaProfileSelector profiles={profiles} value={profileId} onChange={id=>{setProfileId(id);setResult(undefined)}}/><DashaSettings convention={convention} reference={reference} onConvention={value=>{setConvention(value);setResult(undefined)}} onReference={value=>{setReference(value);setResult(undefined)}}/></AppCard>{loadingProfiles||loading?<DashaLoading/>:profiles.length===0?<p className="rounded-2xl bg-[var(--soft)] p-5 text-[var(--muted)]">Create a birth profile with an exact birth time before calculating Vimshottari Dasha.</p>:!profileId?<p className="rounded-2xl bg-[var(--soft)] p-5 text-[var(--muted)]">Select a saved birth profile.</p>:error?<DashaError message={error} onRetry={()=>setRetry(value=>value+1)}/>:result?<DashaDashboard result={result}/>:null}</div>
}

import { useMemo, useState } from 'react'
import type { BirthProfile, MatchingPartnerResult, MatchingRole } from '../../types/api'
import { matchingText } from '../../constants/matchingText'

export function PartnerSelector({number,profiles,value,role,onProfile,onRole,moon}:{number:1|2;profiles:BirthProfile[];value:number|null;role:MatchingRole;onProfile:(id:number|null)=>void;onRole:(role:MatchingRole)=>void;moon?:MatchingPartnerResult}){
 const [query,setQuery]=useState('')
 const filtered=useMemo(()=>profiles.filter(item=>item.full_name.toLowerCase().includes(query.toLowerCase())||item.location.city.toLowerCase().includes(query.toLowerCase())),[profiles,query])
 const selected=profiles.find(item=>item.id===value)
 return <section aria-labelledby={`partner-${number}-heading`} className="rounded-2xl border border-[var(--border)] p-5">
  <h2 id={`partner-${number}-heading`} className="text-lg font-extrabold">Partner {number}</h2>
  <label className="mt-4 block text-sm font-semibold" htmlFor={`partner-${number}-search`}>Search saved profiles</label>
  <input id={`partner-${number}-search`} value={query} onChange={event=>setQuery(event.target.value)} placeholder="Name or birthplace" className="mt-2 w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3 py-2.5"/>
  <label className="mt-4 block text-sm font-semibold" htmlFor={`partner-${number}-profile`}>Birth profile</label>
  <select id={`partner-${number}-profile`} value={value??''} onChange={event=>onProfile(event.target.value?Number(event.target.value):null)} className="mt-2 w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3 py-2.5">
   <option value="">Select a saved profile</option>{filtered.map(item=><option key={item.id} value={item.id}>{item.full_name} · {item.location.city}</option>)}
  </select>
  <fieldset className="mt-4"><legend className="text-sm font-semibold">Traditional calculation role</legend><div className="mt-2 flex flex-wrap gap-3">{(['bride','groom'] as const).map(item=><label key={item} className={`cursor-pointer rounded-xl border px-3 py-2 text-sm ${role===item?'border-[var(--primary)] bg-[var(--primary-soft)]':'border-[var(--border)]'}`}><input type="radio" name={`partner-${number}-role`} value={item} checked={role===item} onChange={()=>onRole(item)} className="mr-2"/>{matchingText.roles[item]}</label>)}</div></fieldset>
  {selected&&<dl className="mt-4 grid gap-2 text-sm"><div><dt className="text-[var(--muted)]">Birth</dt><dd className="font-semibold">{selected.birth_date} · {selected.birth_time_unknown?'Time unknown':selected.birth_time}</dd></div><div><dt className="text-[var(--muted)]">Place</dt><dd className="font-semibold">{selected.location.city}, {selected.location.state&&`${selected.location.state}, `}{selected.location.country}</dd></div>{moon&&<><div><dt className="text-[var(--muted)]">Moon Rashi</dt><dd className="font-semibold">{moon.moon.rashi} · {moon.moon.rashi_lord}</dd></div><div><dt className="text-[var(--muted)]">Nakshatra</dt><dd className="font-semibold">{moon.moon.nakshatra} · Pada {moon.moon.pada}</dd></div></>}</dl>}
 </section>
}

import { Search } from 'lucide-react'
import { useMemo, useState } from 'react'
import type { BirthProfile } from '../../types/api'

export function DashaProfileSelector({profiles,value,onChange}:{profiles:BirthProfile[];value:number|null;onChange:(id:number)=>void}){
 const [search,setSearch]=useState('');const filtered=useMemo(()=>{const term=search.toLowerCase().trim();return term?profiles.filter(profile=>`${profile.full_name} ${profile.location.city}`.toLowerCase().includes(term)):profiles},[profiles,search])
 return <div className="grid min-w-0 gap-4 sm:grid-cols-2"><label className="min-w-0 text-sm font-bold"><span className="flex items-center gap-2"><Search className="size-4"/>Search profiles</span><input value={search} onChange={event=>setSearch(event.target.value)} placeholder="Name or birthplace" className="mt-2 min-h-11 w-full min-w-0 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3"/></label><label className="min-w-0 text-sm font-bold" htmlFor="dasha-profile">Birth profile<select id="dasha-profile" value={value??''} onChange={event=>onChange(Number(event.target.value))} className="mt-2 min-h-11 w-full min-w-0 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3"><option value="">Select a saved profile</option>{filtered.map(profile=><option key={profile.id} value={profile.id}>{profile.full_name} · {profile.birth_date} · {profile.location.city}</option>)}</select></label></div>
}

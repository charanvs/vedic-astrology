import { MapPin, Search } from 'lucide-react'
import { useMemo, useState } from 'react'
import type { Location } from '../../types/api'

export function PanchangLocationSelector({locations,value,onChange}:{locations:Location[];value:number|null;onChange:(location:Location|undefined)=>void}){
 const [search,setSearch]=useState('');const filtered=useMemo(()=>{const term=search.trim().toLowerCase();return term?locations.filter(item=>`${item.city} ${item.state??''} ${item.country}`.toLowerCase().includes(term)):locations},[locations,search])
 return <div className="grid min-w-0 gap-3 sm:grid-cols-2"><label className="min-w-0 text-sm font-bold"><span className="flex items-center gap-2"><Search className="size-4"/>Search stored locations</span><input value={search} onChange={event=>setSearch(event.target.value)} placeholder="City, state, or country" className="mt-2 min-h-11 w-full min-w-0 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3"/></label><label className="min-w-0 text-sm font-bold" htmlFor="panchang-location"><span className="flex items-center gap-2"><MapPin className="size-4"/>Location</span><select id="panchang-location" value={value??''} onChange={event=>onChange(locations.find(item=>item.id===Number(event.target.value)))} className="mt-2 min-h-11 w-full min-w-0 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3"><option value="">Select a stored location</option>{filtered.map(item=><option key={item.id} value={item.id}>{item.city}{item.state?`, ${item.state}`:''}, {item.country}</option>)}</select></label></div>
}

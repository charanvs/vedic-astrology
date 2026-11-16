import { useState } from 'react'
import { apiErrorMessage, createLocation } from '../../services/api'
import type { Location, LocationInput } from '../../types/api'

const input='mt-1.5 min-h-11 w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-[var(--text)]'
const blank:LocationInput={city:'',state:null,country:'',country_code:null,latitude:'',longitude:'',timezone:''}

export function LocationForm({initialCity='',initial,onCreated,onCancel}:{initialCity?:string;initial?:Partial<LocationInput>;onCreated:(location:Location)=>void;onCancel:()=>void}){
 const [values,setValues]=useState<LocationInput>({...blank,city:initialCity,...initial}),[busy,setBusy]=useState(false),[error,setError]=useState('')
 const set=(key:keyof LocationInput,value:string)=>setValues(current=>({...current,[key]:value||null}))
 async function submit(){setError('');if(!values.city?.trim()||!values.country?.trim()||values.latitude===''||values.longitude===''||!values.timezone?.trim()){setError('Complete city, country, latitude, longitude, and IANA timezone before saving the location.');return}setBusy(true);try{onCreated(await createLocation({...values,city:values.city.trim(),country:values.country.trim(),timezone:values.timezone.trim()}))}catch(reason){setError(apiErrorMessage(reason,'Location could not be created.'))}finally{setBusy(false)}}
 function keyDown(event:React.KeyboardEvent){if(event.key==='Enter'){event.preventDefault();event.stopPropagation();if(!busy)void submit()}}
 return <fieldset onKeyDown={keyDown} disabled={busy} className="mt-4 grid gap-3 rounded-2xl border border-[var(--border)] bg-[var(--soft)] p-4 sm:grid-cols-2" aria-label="Create verified location">
  <legend className="sr-only">Create verified location</legend>
  <p className="sm:col-span-2 text-sm text-[var(--muted)]">{initial?.latitude?'Coordinates and timezone were filled in from an offline city database. Review them, then save once you are sure they are correct.':'Enter verified geographic data. Coordinates and timezone are never guessed.'}</p>
  <label className="text-sm font-semibold">City<input required value={values.city} onChange={e=>set('city',e.target.value)} className={input}/></label>
  <label className="text-sm font-semibold">State or province<input value={values.state??''} onChange={e=>set('state',e.target.value)} className={input}/></label>
  <label className="text-sm font-semibold">Country<input required value={values.country} onChange={e=>set('country',e.target.value)} className={input}/></label>
  <label className="text-sm font-semibold">ISO country code<input maxLength={2} placeholder="IN" value={values.country_code??''} onChange={e=>set('country_code',e.target.value)} className={input}/></label>
  <label className="text-sm font-semibold">Latitude<input required type="number" min="-90" max="90" step="0.0000001" value={values.latitude} onChange={e=>set('latitude',e.target.value)} className={input}/></label>
  <label className="text-sm font-semibold">Longitude<input required type="number" min="-180" max="180" step="0.0000001" value={values.longitude} onChange={e=>set('longitude',e.target.value)} className={input}/></label>
  <label className="text-sm font-semibold sm:col-span-2">IANA timezone<input required placeholder="Asia/Kolkata" value={values.timezone} onChange={e=>set('timezone',e.target.value)} className={input}/></label>
  {error&&<div role="alert" aria-label={error} className="fixed right-4 top-4 z-50 w-[min(28rem,calc(100vw-2rem))] rounded-2xl border border-rose-300 bg-rose-50 p-4 font-semibold text-rose-900 shadow-2xl dark:border-rose-800 dark:bg-rose-950 dark:text-rose-100">{error}</div>}
  <div className="flex gap-2 sm:col-span-2"><button type="button" onClick={()=>void submit()} disabled={busy} className="rounded-xl bg-[var(--primary-strong)] px-4 py-2.5 font-bold text-white disabled:opacity-60">{busy?'Saving…':'Save verified location'}</button><button type="button" onClick={onCancel} className="rounded-xl border border-[var(--border)] px-4 py-2.5 font-semibold">Cancel</button></div>
 </fieldset>
}

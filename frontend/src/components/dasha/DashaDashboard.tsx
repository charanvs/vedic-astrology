import { useState } from 'react'
import type { DashaResult } from '../../types/api'
import { AppCard } from '../common/AppCard'
import { CurrentDashaPanel } from './CurrentDashaPanel'
import { DashaBirthBalance } from './DashaBirthBalance'
import { DashaEducation } from './DashaEducation'
import { DashaHierarchy } from './DashaHierarchy'
import { MahadashaTimeline } from './MahadashaTimeline'

export function DashaDashboard({result}:{result:DashaResult}){const [selection,setSelection]=useState<string>();const selected=result.mahadashas.find(item=>item.lord===selection)??result.mahadashas.find(item=>item.active_at_reference)??result.mahadashas[0];return <div className="space-y-6"><AppCard className="p-5"><dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"><div><dt className="text-sm text-[var(--muted)]">Profile</dt><dd className="font-bold">{result.profile.full_name}</dd></div><div><dt className="text-sm text-[var(--muted)]">Birthplace</dt><dd className="font-bold">{result.profile.location.city}, {result.profile.location.country}</dd></div><div><dt className="text-sm text-[var(--muted)]">Birth Nakshatra</dt><dd className="font-bold">{result.birth_moon.nakshatra} · {result.birth_moon.lord}</dd></div><div><dt className="text-sm text-[var(--muted)]">Birth Moon Rashi</dt><dd className="font-bold">{result.birth_moon.rashi.name}</dd></div></dl></AppCard><DashaBirthBalance result={result}/><CurrentDashaPanel result={result}/><AppCard className="p-5 sm:p-6"><MahadashaTimeline periods={result.mahadashas} timezone={result.profile.timezone} selected={selected.lord} onSelect={setSelection}/></AppCard><AppCard className="p-5 sm:p-6"><DashaHierarchy key={selected.lord} mahadasha={selected} timezone={result.profile.timezone}/></AppCard><DashaEducation/></div>}

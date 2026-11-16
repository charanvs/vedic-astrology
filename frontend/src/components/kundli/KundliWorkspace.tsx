import { AlertTriangle, Orbit } from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'
import { apiErrorMessage, calculateBirthProfile } from '../../services/api'
import type { AstrologyCalculation, BirthProfile } from '../../types/api'
import { AppCard } from '../common/AppCard'
import { KundliControls } from './KundliControls'
import { KundliLegend } from './KundliLegend'
import { NorthIndianKundli } from './NorthIndianKundli'
import { transformKundliData } from './transformKundliData'
import type { KundliDisplayMode } from './kundliTypes'
import { exportKundliSvg } from './exportKundliSvg'

export function KundliWorkspace({ profile }: { profile: BirthProfile }) {
  const [result, setResult] = useState<AstrologyCalculation>()
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [mode, setMode] = useState<KundliDisplayMode>('standard')
  const [showHouseNumbers, setShowHouseNumbers] = useState(true)
  const [selectedHouse, setSelectedHouse] = useState(1)
  const [selectedPlanet, setSelectedPlanet] = useState<string | null>(null)
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    setResult(undefined); setError(''); setSelectedHouse(1); setSelectedPlanet(null)
    if (profile.birth_time_unknown) return
    let active = true
    setLoading(true)
    calculateBirthProfile(profile.id).then((value) => { if (active) setResult(value) }).catch((reason) => { if (active) setError(apiErrorMessage(reason, 'Kundli could not be calculated.')) }).finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [profile])

  const { chart, chartError } = useMemo(() => {
    if (!result) return { chart: undefined, chartError: '' }
    try { return { chart: transformKundliData(result), chartError: '' } } catch (reason) { return { chart: undefined, chartError: reason instanceof Error ? reason.message : 'Invalid chart data.' } }
  }, [result])

  if (profile.birth_time_unknown) return <AppCard className="p-5"><div className="flex gap-3 text-amber-800 dark:text-amber-200"><AlertTriangle className="size-5 shrink-0" aria-hidden="true" /><p><strong>Exact birth time required.</strong> A complete Janam Kundli cannot be generated when birth time is unknown.</p></div></AppCard>
  if (loading) return <p role="status" className="text-[var(--muted)]">Generating North Indian Kundli…</p>
  if (error || chartError) return <p role="alert" className="rounded-xl bg-rose-50 p-4 text-rose-800 dark:bg-rose-950 dark:text-rose-200">{error || chartError}</p>
  if (!chart) return null

  const house = chart.houses[selectedHouse - 1]
  const planet = selectedPlanet ? chart.planets.find((item) => item.identifier === selectedPlanet) : undefined
  const selectPlanet = (identifier: string) => {
    const next = chart.planets.find((item) => item.identifier === identifier)
    setSelectedPlanet(identifier)
    if (next) setSelectedHouse(next.house)
  }
  const exportSvg = () => {
    exportKundliSvg(svgRef.current, `kundli-profile-${profile.id}.svg`, `Vedic Astrology Kundli; profile reference ${profile.id}`)
  }

  return <section className="space-y-5" aria-labelledby="kundli-heading">
    <AppCard className="p-5 sm:p-6">
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-start">
        <div><h2 id="kundli-heading" className="flex items-center gap-2 text-xl font-bold"><Orbit className="size-5 text-[var(--primary-strong)]" />North Indian Janam Kundli</h2><p className="mt-1 text-sm text-[var(--muted)]">{profile.full_name} · {profile.birth_date} {profile.birth_time?.slice(0, 8)} · {profile.location.city}, {profile.location.country}</p></div>
        <KundliControls mode={mode} showHouseNumbers={showHouseNumbers} onModeChange={setMode} onHouseNumbersChange={setShowHouseNumbers} onExport={exportSvg} />
      </div>
      <div className="mt-6 grid items-start gap-6 xl:grid-cols-[minmax(0,720px)_minmax(260px,1fr)]">
        <div className="mx-auto w-full"><NorthIndianKundli ref={svgRef} data={chart} displayMode={mode} showHouseNumbers={showHouseNumbers} selectedHouse={selectedHouse} selectedPlanet={selectedPlanet} onSelectHouse={(value) => { setSelectedHouse(value); setSelectedPlanet(null) }} onSelectPlanet={selectPlanet} /><div className="mt-4"><KundliLegend /></div></div>
        <div className="space-y-4">
          <div className="rounded-2xl bg-[var(--soft)] p-4"><p className="text-xs font-bold uppercase tracking-wide text-[var(--muted)]">Selected house</p><h3 className="mt-1 text-lg font-extrabold">House {house.house_number} · {house.rashi_name}</h3><p className="text-sm text-[var(--muted)]">{house.rashi_english_name} · {house.rashi_hindi_name}</p><p className="mt-3 text-sm"><strong>Grahas:</strong> {house.planets.length ? house.planets.map((item) => item.english_name).join(', ') : 'None'}</p>{house.is_lagna && <p className="mt-2 text-sm font-bold text-[var(--primary-strong)]">Lagna house</p>}</div>
          {planet && <div className="rounded-2xl border border-[var(--border)] p-4"><p className="text-xs font-bold uppercase tracking-wide text-[var(--muted)]">Selected graha</p><h3 className="mt-1 text-lg font-extrabold">{planet.english_name} · {planet.sanskrit_name}</h3><dl className="mt-3 grid grid-cols-2 gap-3 text-sm"><div><dt className="text-[var(--muted)]">Longitude</dt><dd className="font-semibold">{planet.longitude_formatted}</dd></div><div><dt className="text-[var(--muted)]">Motion</dt><dd className="font-semibold capitalize">{planet.motion}</dd></div><div><dt className="text-[var(--muted)]">Nakshatra</dt><dd className="font-semibold">{planet.nakshatra.name}</dd></div><div><dt className="text-[var(--muted)]">Pada</dt><dd className="font-semibold">{planet.nakshatra.pada}</dd></div></dl></div>}
          <dl className="grid grid-cols-2 gap-3 rounded-2xl border border-[var(--border)] p-4 text-sm"><div><dt className="text-[var(--muted)]">Lagna</dt><dd className="font-bold">{chart.lagna.rashi.name}</dd></div><div><dt className="text-[var(--muted)]">Lagna degree</dt><dd className="font-bold">{chart.lagna.longitude_formatted}</dd></div><div><dt className="text-[var(--muted)]">Ayanamsa</dt><dd className="font-bold">{chart.ayanamsa.formatted}</dd></div><div><dt className="text-[var(--muted)]">Zodiac</dt><dd className="font-semibold capitalize">{chart.settings.zodiac}</dd></div><div><dt className="text-[var(--muted)]">Node</dt><dd className="font-semibold capitalize">{chart.settings.node_convention}</dd></div><div><dt className="text-[var(--muted)]">Houses</dt><dd className="font-semibold">Whole sign</dd></div></dl>
        </div>
      </div>
    </AppCard>
    <AppCard className="overflow-hidden"><div className="overflow-x-auto"><table className="w-full min-w-[860px] text-left text-sm"><caption className="sr-only">Kundli planetary positions</caption><thead className="bg-[var(--soft)]"><tr>{['Graha', 'Rashi', 'Longitude', 'Degree in Rashi', 'Nakshatra', 'Pada', 'House', 'Motion'].map((label) => <th key={label} className="px-4 py-3">{label}</th>)}</tr></thead><tbody>{chart.planets.map((item) => <tr key={item.identifier} tabIndex={0} aria-selected={selectedPlanet === item.identifier} onClick={() => selectPlanet(item.identifier)} onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); selectPlanet(item.identifier) } }} className={`cursor-pointer border-t border-[var(--border)] ${selectedPlanet === item.identifier ? 'bg-[var(--primary-soft)]' : 'hover:bg-[var(--soft)]'}`}><td className="px-4 py-3 font-bold">{item.english_name}<span className="block text-xs font-normal text-[var(--muted)]">{item.sanskrit_name}</span></td><td className="px-4 py-3">{item.rashi.name}</td><td className="px-4 py-3 tabular-nums">{item.longitude_formatted}</td><td className="px-4 py-3 tabular-nums">{item.rashi.longitude_within.toFixed(6)}°</td><td className="px-4 py-3">{item.nakshatra.name}</td><td className="px-4 py-3">{item.nakshatra.pada}</td><td className="px-4 py-3">{item.house}</td><td className="px-4 py-3 capitalize">{item.motion}{item.retrograde ? ' (R)' : ''}</td></tr>)}</tbody></table></div></AppCard>
    <p className="text-sm text-[var(--muted)]">Astronomical calculations use Swiss Ephemeris with Lahiri ayanamsa. This chart provides positions only, not predictive interpretation.</p>
  </section>
}

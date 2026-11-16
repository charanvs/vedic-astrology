import { useMemo, useRef, useState } from 'react'
import type { AstrologyCalculation, BirthProfile, DivisionalChart } from '../../types/api'
import { KundliControls } from '../kundli/KundliControls'
import { NorthIndianKundli } from '../kundli/NorthIndianKundli'
import { exportKundliSvg } from '../kundli/exportKundliSvg'
import type { KundliDisplayMode } from '../kundli/kundliTypes'
import { transformKundliData } from '../kundli/transformKundliData'
import { DivisionalDetails } from './DivisionalDetails'
import { DivisionalPlanetTable } from './DivisionalPlanetTable'

export function DivisionalChartPanel({ chart, profile, compact = false }: { chart: AstrologyCalculation | DivisionalChart; profile: BirthProfile; compact?: boolean }) {
  const type = 'chart_type' in chart ? chart.chart_type : 'D1', name = 'chart_type' in chart ? chart.chart_name : 'Rashi'
  const data = useMemo(() => transformKundliData(chart), [chart])
  const [mode, setMode] = useState<KundliDisplayMode>('standard'), [showNumbers, setShowNumbers] = useState(true)
  const [house, setHouse] = useState(1), [planet, setPlanet] = useState<string | null>(null)
  const svgRef = useRef<SVGSVGElement>(null)
  const selectPlanet = (identifier: string) => { setPlanet(identifier); const found = data.planets.find(item => item.identifier === identifier); if (found) setHouse(found.house) }
  return <section className="min-w-0 space-y-4" aria-label={`${type} ${name} chart`}>
    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"><div><h2 className="text-xl font-extrabold">{type} · {name}</h2><p className="text-sm text-[var(--muted)]">{'chart_type' in chart ? chart.primary_use : 'Sidereal birth chart'}</p></div><KundliControls mode={mode} showHouseNumbers={showNumbers} onModeChange={setMode} onHouseNumbersChange={setShowNumbers} onExport={() => exportKundliSvg(svgRef.current, `${profile.full_name.toLowerCase().replaceAll(' ', '-')}-${type.toLowerCase()}.svg`, `${type} ${name}; profile reference ${profile.id}; Lahiri sidereal, mean node, whole-sign houses`)} /></div>
    <div className="mx-auto max-w-[720px]"><NorthIndianKundli ref={svgRef} data={data} displayMode={mode} showHouseNumbers={showNumbers} selectedHouse={house} selectedPlanet={planet} onSelectHouse={value => { setHouse(value); setPlanet(null) }} onSelectPlanet={selectPlanet} chartTitle={`${type} ${name} North Indian Kundli`} chartDescription={`${type} ${name} chart for ${profile.full_name}, rendered with whole-sign houses.`}/></div>
    <DivisionalDetails chart={chart}/>{!compact && <DivisionalPlanetTable chart={chart}/>} 
  </section>
}

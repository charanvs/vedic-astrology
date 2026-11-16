import { forwardRef, useId } from 'react'
import { geometryForHouse, KUNDLI_VIEWBOX } from './kundliGeometry'
import { KundliHouse } from './KundliHouse'
import type { KundliChartData, KundliDisplayMode } from './kundliTypes'

type Props = {
  data: KundliChartData
  displayMode: KundliDisplayMode
  showHouseNumbers: boolean
  selectedHouse: number
  selectedPlanet: string | null
  onSelectHouse: (houseNumber: number) => void
  onSelectPlanet: (identifier: string) => void
  chartTitle?: string
  chartDescription?: string
}

export const NorthIndianKundli = forwardRef<SVGSVGElement, Props>(function NorthIndianKundli({ data, displayMode, showHouseNumbers, selectedHouse, selectedPlanet, onSelectHouse, onSelectPlanet, chartTitle = 'North Indian Janam Kundli', chartDescription = 'Twelve fixed houses in the North Indian diamond layout. House one is at the top, house four at the left, house seven at the bottom, and house ten at the right. Houses proceed anticlockwise.' }, ref) {
  const id = useId().replaceAll(':', '')
  const titleId = `kundli-title-${id}`, descriptionId = `kundli-description-${id}`
  return <svg ref={ref} viewBox={`0 0 ${KUNDLI_VIEWBOX} ${KUNDLI_VIEWBOX}`} role="img" aria-labelledby={`${titleId} ${descriptionId}`} className="aspect-square w-full max-w-[720px] bg-[var(--surface)]" xmlns="http://www.w3.org/2000/svg">
    <title id={titleId}>{chartTitle}</title>
    <desc id={descriptionId}>{chartDescription}</desc>
    {data.houses.map((house) => <KundliHouse key={house.house_number} house={house} geometry={geometryForHouse(house.house_number)} displayMode={displayMode} showHouseNumbers={showHouseNumbers} selected={selectedHouse === house.house_number} selectedPlanet={selectedPlanet} onSelectHouse={onSelectHouse} onSelectPlanet={onSelectPlanet} />)}
    <g className="pointer-events-none fill-none stroke-[var(--border)]" strokeWidth="2" vectorEffect="non-scaling-stroke" aria-hidden="true">
      <line x1="0" y1="0" x2="600" y2="600" />
      <line x1="600" y1="0" x2="0" y2="600" />
      <polygon points="300,0 600,300 300,600 0,300" />
    </g>
    <rect x="1" y="1" width="598" height="598" fill="none" className="pointer-events-none stroke-[var(--primary-strong)]" strokeWidth="3" vectorEffect="non-scaling-stroke" />
  </svg>
})

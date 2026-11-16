import type { KeyboardEvent } from 'react'
import { planetLabelPosition } from './kundliGeometry'
import { PlanetLabel } from './PlanetLabel'
import type { HouseGeometry, KundliDisplayMode, KundliHouse } from './kundliTypes'

type Props = {
  house: KundliHouse
  geometry: HouseGeometry
  displayMode: KundliDisplayMode
  showHouseNumbers: boolean
  selected: boolean
  selectedPlanet: string | null
  onSelectHouse: (houseNumber: number) => void
  onSelectPlanet: (identifier: string) => void
}

export function KundliHouse({ house, geometry, displayMode, showHouseNumbers, selected, selectedPlanet, onSelectHouse, onSelectPlanet }: Props) {
  const activate = (event: KeyboardEvent<SVGGElement>) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      onSelectHouse(house.house_number)
    }
  }
  const description = `House ${house.house_number}, ${house.rashi_english_name}, ${house.planets.length ? house.planets.map((planet) => planet.english_name).join(', ') : 'no planets'}`
  return <g className="kundli-house cursor-pointer" role="button" tabIndex={0} aria-label={description} aria-pressed={selected} data-house-number={house.house_number} onClick={() => onSelectHouse(house.house_number)} onKeyDown={activate}>
    <title>{description}</title>
    <polygon points={geometry.polygon} className={`kundli-region stroke-[var(--border)] transition-colors ${selected ? 'fill-[var(--primary-soft)]' : 'fill-[var(--surface)] hover:fill-[var(--soft)]'}`} strokeWidth={selected ? 4 : 2} vectorEffect="non-scaling-stroke" />
    {showHouseNumbers && <text x={geometry.label.x} y={geometry.label.y - 12} textAnchor="middle" className="pointer-events-none fill-[var(--muted)] text-[12px] font-semibold">H{house.house_number}</text>}
    <text x={geometry.label.x} y={geometry.label.y + (showHouseNumbers ? 8 : 0)} textAnchor="middle" className="pointer-events-none fill-[var(--primary-strong)] text-[18px] font-extrabold">{house.rashi_number}</text>
    {displayMode === 'detailed' && <text x={geometry.label.x} y={geometry.label.y + (showHouseNumbers ? 25 : 18)} textAnchor="middle" className="pointer-events-none fill-[var(--muted)] text-[11px] font-semibold">{house.rashi_name}</text>}
    {house.is_lagna && <text x={geometry.label.x} y={geometry.label.y + (showHouseNumbers ? 42 : 35)} textAnchor="middle" className="pointer-events-none fill-[var(--primary-strong)] text-[12px] font-bold">Lagna</text>}
    {house.planets.map((planet, index) => <PlanetLabel key={planet.identifier} planet={planet} position={planetLabelPosition(geometry.planetAnchor, index, house.planets.length)} displayMode={displayMode} selected={selectedPlanet === planet.identifier} onSelect={onSelectPlanet} />)}
  </g>
}

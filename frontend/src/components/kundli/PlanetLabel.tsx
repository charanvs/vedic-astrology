import type { KeyboardEvent } from 'react'
import type { KundliDisplayMode, KundliPlanet, Point } from './kundliTypes'

type Props = {
  planet: KundliPlanet
  position: Point
  displayMode: KundliDisplayMode
  selected: boolean
  onSelect: (identifier: string) => void
}

export function PlanetLabel({ planet, position, displayMode, selected, onSelect }: Props) {
  const suffix = displayMode === 'detailed' && planet.retrograde ? ' (R)' : displayMode === 'detailed' && planet.motion === 'stationary' ? ' (S)' : ''
  const activate = (event: KeyboardEvent<SVGGElement>) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      event.stopPropagation()
      onSelect(planet.identifier)
    }
  }
  return <g className="kundli-planet cursor-pointer" role="button" tabIndex={0} aria-label={`${planet.english_name}, ${planet.rashi.name}, house ${planet.house}${planet.retrograde ? ', retrograde' : ''}`} aria-pressed={selected} onClick={(event) => { event.stopPropagation(); onSelect(planet.identifier) }} onKeyDown={activate}>
    <title>{planet.english_name}: {planet.longitude_formatted}, {planet.nakshatra.name} pada {planet.nakshatra.pada}</title>
    {selected && <circle cx={position.x} cy={position.y - 5} r="18" className="fill-[var(--primary-soft)] stroke-[var(--primary)]" strokeWidth="2" />}
    <text x={position.x} y={position.y} textAnchor="middle" className="select-none fill-[var(--text)] text-[16px] font-bold">{planet.abbreviation}{suffix}</text>
  </g>
}

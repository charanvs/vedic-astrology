import type { AstrologyCalculation, ChartHouse, PlanetaryPosition } from '../../types/api'

export type KundliDisplayMode = 'standard' | 'detailed'

export type Point = {
  x: number
  y: number
}

export type HouseGeometry = {
  houseNumber: number
  polygon: string
  label: Point
  planetAnchor: Point
  description: string
}

export type KundliPlanet = PlanetaryPosition & {
  abbreviation: string
}

export type KundliHouse = ChartHouse & {
  planets: KundliPlanet[]
}

export type KundliChartData = {
  lagna: AstrologyCalculation['lagna']
  houses: KundliHouse[]
  planets: KundliPlanet[]
  settings: AstrologyCalculation['settings']
  ayanamsa: AstrologyCalculation['ayanamsa']
  engine: AstrologyCalculation['engine']
}

import type { AstrologyCalculation } from '../../types/api'
import type { KundliChartData, KundliPlanet } from './kundliTypes'

const PLANET_ABBREVIATIONS: Record<string, string> = {
  sun: 'Su', moon: 'Mo', mars: 'Ma', mercury: 'Me', jupiter: 'Ju',
  venus: 'Ve', saturn: 'Sa', rahu: 'Ra', ketu: 'Ke',
}

export function transformKundliData(calculation: AstrologyCalculation): KundliChartData {
  const sortedHouses = [...calculation.houses].sort((a, b) => a.house_number - b.house_number)
  if (sortedHouses.length !== 12 || sortedHouses.some((house, index) => house.house_number !== index + 1)) {
    throw new Error('The chart response must contain houses 1 through 12 exactly once.')
  }

  sortedHouses.forEach((house, index) => {
    const expectedRashi = ((calculation.lagna.rashi.number - 1 + index) % 12) + 1
    if (house.rashi_number !== expectedRashi) {
      throw new Error(`House ${house.house_number} has an invalid Rashi assignment.`)
    }
  })

  const seenPlanets = new Set<string>()
  const planets: KundliPlanet[] = calculation.planets.map((planet) => {
    const identifier = planet.identifier.toLowerCase()
    const abbreviation = PLANET_ABBREVIATIONS[identifier]
    if (!abbreviation) throw new Error(`Unsupported planet identifier: ${planet.identifier}.`)
    if (seenPlanets.has(identifier)) throw new Error(`Planet ${planet.english_name} appears more than once.`)
    seenPlanets.add(identifier)
    return { ...planet, abbreviation }
  })

  const byIdentifier = new Map(planets.map((planet) => [planet.identifier.toLowerCase(), planet]))
  const placed = new Set<string>()
  const houses = sortedHouses.map((house) => {
    const housePlanets = house.planet_identifiers.map((rawIdentifier) => {
      const identifier = rawIdentifier.toLowerCase()
      const planet = byIdentifier.get(identifier)
      if (!planet) throw new Error(`House ${house.house_number} references unknown planet ${rawIdentifier}.`)
      if (placed.has(identifier)) throw new Error(`Planet ${planet.english_name} is placed in more than one house.`)
      if (planet.house !== house.house_number || planet.rashi.number !== house.rashi_number) {
        throw new Error(`Planet ${planet.english_name} does not match its house assignment.`)
      }
      placed.add(identifier)
      return planet
    })
    return { ...house, planets: housePlanets }
  })

  if (placed.size !== planets.length) throw new Error('Every planet must be placed in exactly one house.')

  return {
    lagna: calculation.lagna,
    houses,
    planets,
    settings: calculation.settings,
    ayanamsa: calculation.ayanamsa,
    engine: calculation.engine,
  }
}

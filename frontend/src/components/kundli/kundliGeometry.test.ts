import { describe, expect, it } from 'vitest'
import { HOUSE_GEOMETRY, planetLabelPosition } from './kundliGeometry'
import { makeKundliCalculation } from './kundliTestFixture'
import { transformKundliData } from './transformKundliData'

describe('North Indian Kundli geometry and mapping', () => {
  it('uses twelve fixed anticlockwise houses with canonical cardinal positions', () => {
    expect(HOUSE_GEOMETRY.map((item) => item.houseNumber)).toEqual([1,2,3,4,5,6,7,8,9,10,11,12])
    expect(HOUSE_GEOMETRY[0].label.y).toBeLessThan(100)
    expect(HOUSE_GEOMETRY[3].label.x).toBeLessThan(100)
    expect(HOUSE_GEOMETRY[6].label.y).toBeGreaterThan(500)
    expect(HOUSE_GEOMETRY[9].label.x).toBeGreaterThan(500)
    expect(HOUSE_GEOMETRY[1].description).toContain('upper-left')
    expect(HOUSE_GEOMETRY[11].description).toContain('upper-right')
  })

  it.each([1,7,10])('maps houses from Lagna Rashi %s with wraparound', (lagnaRashi) => {
    const chart = transformKundliData(makeKundliCalculation(lagnaRashi))
    expect(chart.houses.map((house) => house.rashi_number)).toEqual(Array.from({length:12},(_,index)=>((lagnaRashi-1+index)%12)+1))
    expect(chart.houses[0].planets[0].identifier).toBe('moon')
  })

  it('rejects an invalid backend Rashi assignment', () => {
    const calculation = makeKundliCalculation()
    calculation.houses[4].rashi_number = 12
    expect(() => transformKundliData(calculation)).toThrow(/invalid Rashi assignment/)
  })

  it('lays multiple planet labels out without identical coordinates', () => {
    const points = Array.from({length:7},(_,index)=>planetLabelPosition({x:300,y:300},index,7))
    expect(new Set(points.map((point)=>`${point.x},${point.y}`)).size).toBe(7)
  })
})

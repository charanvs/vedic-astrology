import type { HouseGeometry, Point } from './kundliTypes'

export const KUNDLI_VIEWBOX = 600

export const HOUSE_GEOMETRY: HouseGeometry[] = [
  { houseNumber: 1, polygon: '300,0 450,150 300,300 150,150', label: { x: 300, y: 58 }, planetAnchor: { x: 300, y: 175 }, description: 'First house, top central diamond' },
  { houseNumber: 2, polygon: '0,0 300,0 150,150', label: { x: 150, y: 30 }, planetAnchor: { x: 150, y: 88 }, description: 'Second house, upper-left triangle' },
  { houseNumber: 3, polygon: '0,0 150,150 0,300', label: { x: 28, y: 150 }, planetAnchor: { x: 88, y: 150 }, description: 'Third house, left upper triangle' },
  { houseNumber: 4, polygon: '0,300 150,150 300,300 150,450', label: { x: 72, y: 300 }, planetAnchor: { x: 170, y: 300 }, description: 'Fourth house, left central diamond' },
  { houseNumber: 5, polygon: '0,300 150,450 0,600', label: { x: 28, y: 450 }, planetAnchor: { x: 88, y: 450 }, description: 'Fifth house, left lower triangle' },
  { houseNumber: 6, polygon: '0,600 300,600 150,450', label: { x: 150, y: 570 }, planetAnchor: { x: 150, y: 512 }, description: 'Sixth house, lower-left triangle' },
  { houseNumber: 7, polygon: '300,300 450,450 300,600 150,450', label: { x: 300, y: 542 }, planetAnchor: { x: 300, y: 425 }, description: 'Seventh house, bottom central diamond' },
  { houseNumber: 8, polygon: '300,600 600,600 450,450', label: { x: 450, y: 570 }, planetAnchor: { x: 450, y: 512 }, description: 'Eighth house, lower-right triangle' },
  { houseNumber: 9, polygon: '600,600 600,300 450,450', label: { x: 572, y: 450 }, planetAnchor: { x: 512, y: 450 }, description: 'Ninth house, right lower triangle' },
  { houseNumber: 10, polygon: '300,300 450,150 600,300 450,450', label: { x: 528, y: 300 }, planetAnchor: { x: 430, y: 300 }, description: 'Tenth house, right central diamond' },
  { houseNumber: 11, polygon: '600,300 600,0 450,150', label: { x: 572, y: 150 }, planetAnchor: { x: 512, y: 150 }, description: 'Eleventh house, right upper triangle' },
  { houseNumber: 12, polygon: '300,0 600,0 450,150', label: { x: 450, y: 30 }, planetAnchor: { x: 450, y: 88 }, description: 'Twelfth house, upper-right triangle' },
]

export function geometryForHouse(houseNumber: number): HouseGeometry {
  const geometry = HOUSE_GEOMETRY.find((house) => house.houseNumber === houseNumber)
  if (!geometry) throw new Error(`No Kundli geometry exists for house ${houseNumber}.`)
  return geometry
}

export function planetLabelPosition(anchor: Point, index: number, total: number): Point {
  const columns = Math.min(3, total)
  const rows = Math.ceil(total / columns)
  const row = Math.floor(index / columns)
  const column = index % columns
  const itemsInRow = Math.min(columns, total - row * columns)
  return {
    x: anchor.x + (column - (itemsInRow - 1) / 2) * 42,
    y: anchor.y + (row - (rows - 1) / 2) * 22,
  }
}

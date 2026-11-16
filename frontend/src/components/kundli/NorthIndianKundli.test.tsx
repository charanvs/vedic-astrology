import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { KundliControls } from './KundliControls'
import { NorthIndianKundli } from './NorthIndianKundli'
import { makeKundliCalculation } from './kundliTestFixture'
import { transformKundliData } from './transformKundliData'

const data = transformKundliData(makeKundliCalculation())

describe('NorthIndianKundli', () => {
  it('renders all houses, Lagna, and each planet once', () => {
    const { container } = render(<NorthIndianKundli data={data} displayMode="standard" showHouseNumbers selectedHouse={1} selectedPlanet={null} onSelectHouse={vi.fn()} onSelectPlanet={vi.fn()} />)
    expect(container.querySelectorAll('[data-house-number]')).toHaveLength(12)
    expect(screen.getByText('Lagna')).toBeInTheDocument()
    expect(screen.getAllByText('Mo')).toHaveLength(1)
  })

  it('uses unique accessible labels when multiple charts are rendered', () => {
    const props={data,displayMode:'standard' as const,showHouseNumbers:true,selectedHouse:1,selectedPlanet:null,onSelectHouse:vi.fn(),onSelectPlanet:vi.fn()}
    const { container } = render(<><NorthIndianKundli {...props} chartTitle="D1 Rashi"/><NorthIndianKundli {...props} chartTitle="D9 Navamsha"/></>)
    const svgs = [...container.querySelectorAll('svg')]
    expect(svgs).toHaveLength(2)
    expect(svgs[0].getAttribute('aria-labelledby')).not.toBe(svgs[1].getAttribute('aria-labelledby'))
    expect(screen.getByText('D1 Rashi')).toBeInTheDocument(); expect(screen.getByText('D9 Navamsha')).toBeInTheDocument()
  })

  it('supports mouse and keyboard house selection', async () => {
    const selectHouse = vi.fn(); const user = userEvent.setup()
    render(<NorthIndianKundli data={data} displayMode="standard" showHouseNumbers selectedHouse={1} selectedPlanet={null} onSelectHouse={selectHouse} onSelectPlanet={vi.fn()} />)
    const house4 = screen.getByRole('button', { name: /House 4/ })
    await user.click(house4); expect(selectHouse).toHaveBeenCalledWith(4)
    fireEvent.keyDown(house4, { key:'Enter' }); expect(selectHouse).toHaveBeenLastCalledWith(4)
  })

  it('shows retrograde notation only in detailed mode', () => {
    const props={data,showHouseNumbers:true,selectedHouse:1,selectedPlanet:null,onSelectHouse:vi.fn(),onSelectPlanet:vi.fn()}
    const { rerender } = render(<NorthIndianKundli {...props} displayMode="standard" />)
    expect(screen.queryByText('Mo (R)')).not.toBeInTheDocument()
    rerender(<NorthIndianKundli {...props} displayMode="detailed" />)
    expect(screen.getByText('Mo (R)')).toBeInTheDocument()
  })

  it('exposes functional display and export controls', async () => {
    const setMode=vi.fn(), setNumbers=vi.fn(), exportSvg=vi.fn(), user=userEvent.setup()
    render(<KundliControls mode="standard" showHouseNumbers onModeChange={setMode} onHouseNumbersChange={setNumbers} onExport={exportSvg} />)
    await user.click(screen.getByRole('button',{name:'Detailed'})); expect(setMode).toHaveBeenCalledWith('detailed')
    await user.click(screen.getByRole('checkbox',{name:'House numbers'})); expect(setNumbers).toHaveBeenCalledWith(false)
    await user.click(screen.getByRole('button',{name:/Export SVG/})); expect(exportSvg).toHaveBeenCalled()
  })
})

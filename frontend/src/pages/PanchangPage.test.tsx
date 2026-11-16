import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as api from '../services/api'
import { locationToday } from '../components/panchang/panchangFormat'
import { panchangLocation, panchangResult } from '../components/panchang/panchangTestFixture'
import { PanchangPage } from './PanchangPage'

describe('PanchangPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    vi.spyOn(api, 'getLocations').mockResolvedValue([panchangLocation])
    vi.spyOn(api, 'getDailyPanchang').mockResolvedValue(panchangResult)
  })

  it('renders five selectable Panchang cards, solar data, and multiple timeline events', async () => {
    const user = userEvent.setup()
    render(<PanchangPage />)
    expect((await screen.findAllByText('Shukla Chaturthi')).length).toBeGreaterThan(0)
    for (const label of ['Tithi', 'Vara', 'Nakshatra', 'Yoga', 'Karana']) {
      expect(screen.getByRole('button', { name: new RegExp(`^${label}:`) })).toBeInTheDocument()
    }
    expect(screen.getAllByText(/06:47/).length).toBeGreaterThan(0)
    expect(screen.getByText('Vanija → Vishti')).toBeInTheDocument()
    expect(screen.getByText('Vishti → Bava')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /^Nakshatra:/ }))
    expect(screen.getByText(/Pada:/)).toBeInTheDocument()
    expect(screen.getByText(/Lord:/)).toBeInTheDocument()
  })

  it('navigates previous, next, and location-relative today dates', async () => {
    const user = userEvent.setup()
    render(<PanchangPage />)
    await screen.findAllByText('Shukla Chaturthi')
    await user.click(screen.getByRole('button', { name: 'Previous day' }))
    expect(api.getDailyPanchang).toHaveBeenLastCalledWith(
      expect.stringMatching(/^\d{4}-\d{2}-\d{2}$/),
      7,
      expect.any(AbortSignal),
    )
    await user.click(screen.getByRole('button', { name: 'Next day' }))
    await user.click(screen.getByRole('button', { name: 'Today' }))
    expect(screen.getByLabelText('Panchang date')).toHaveValue(locationToday('Asia/Kolkata'))
  })

  it('filters and selects stored locations accessibly', async () => {
    const user = userEvent.setup()
    const delhi = { ...panchangLocation, id: 8, city: 'New Delhi' }
    vi.mocked(api.getLocations).mockResolvedValue([panchangLocation, delhi])
    render(<PanchangPage />)
    await user.type(await screen.findByPlaceholderText('City, state, or country'), 'Delhi')
    expect(screen.getByRole('option', { name: /New Delhi/ })).toBeInTheDocument()
    expect(screen.queryByRole('option', { name: /Chandigarh, Chandigarh/ })).not.toBeInTheDocument()
  })

  it('shows a loading state while locations are being loaded', async () => {
    vi.mocked(api.getLocations).mockReturnValue(new Promise(() => {}))
    render(<PanchangPage />)
    expect(await screen.findByText(/Calculating sunrise-anchored/)).toBeInTheDocument()
  })

  it('shows retryable API errors without fabricated values', async () => {
    vi.mocked(api.getDailyPanchang).mockRejectedValue(new Error('offline'))
    const user = userEvent.setup()
    render(<PanchangPage />)
    expect(await screen.findByRole('alert')).toHaveTextContent('Daily Panchang could not be calculated')
    expect(screen.queryByText('Shukla Chaturthi')).not.toBeInTheDocument()
    vi.mocked(api.getDailyPanchang).mockResolvedValue(panchangResult)
    await user.click(screen.getByRole('button', { name: 'Retry' }))
    expect((await screen.findAllByText('Shukla Chaturthi')).length).toBeGreaterThan(0)
  })

  it('shows an explicit missing-sunrise response', async () => {
    vi.mocked(api.getDailyPanchang).mockRejectedValue(
      Object.assign(new Error('missing sunrise'), {
        isAxiosError: true,
        response: { data: { detail: 'Sunrise is unavailable for this location and local civil date' } },
      }),
    )
    render(<PanchangPage />)
    expect(await screen.findByRole('alert')).toHaveTextContent('Sunrise is unavailable')
  })
})

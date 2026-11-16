import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { BirthProfile, Location } from '../types/api'

const location: Location = { id: 1, city: 'Sangrur', state: 'Punjab', country: 'India', country_code: 'IN', latitude: '30.2500000', longitude: '75.8400000', timezone: 'Asia/Kolkata', created_at: '2026-01-01T00:00:00' }
const existing: BirthProfile = { id: 3, user_id: null, full_name: 'Existing Person', gender: null, birth_date: '1980-01-01', birth_time: '10:00:00', birth_time_unknown: false, location_id: 1, location, birth_time_utc: '1980-01-01T04:30:00', utc_offset_minutes: 330, timezone_resolution_status: 'resolved', timezone_fold: null, notes: null, created_at: '2026-01-01T00:00:00', updated_at: '2026-01-01T00:00:00' }
const created: BirthProfile = { ...existing, id: 7, full_name: 'New Person' }

vi.mock('../services/api', () => ({
  getBirthProfiles: vi.fn(async () => [existing]),
  getBirthProfile: vi.fn(),
  apiErrorMessage: vi.fn((_reason: unknown, fallback: string) => fallback),
}))
vi.mock('../components/kundli/KundliWorkspace', () => ({ KundliWorkspace: () => <div>Chart workspace</div> }))
vi.mock('../components/profiles/BirthProfileForm', () => ({
  BirthProfileForm: ({ profile, onSaved }: { profile?: BirthProfile; onSaved: (saved: BirthProfile) => void }) =>
    <button onClick={() => onSaved(created)}>{profile ? 'Simulate update' : 'Simulate create'}</button>,
}))

import { KundliPage } from './KundliPage'

describe('KundliPage profile creation flow', () => {
  beforeEach(() => vi.clearAllMocks())

  it('keeps create mode and confirms the committed profile instead of silently switching to edit mode', async () => {
    const user = userEvent.setup()
    render(<MemoryRouter initialEntries={['/kundli']}><KundliPage /></MemoryRouter>)
    await user.click(await screen.findByRole('button', { name: 'Simulate create' }))
    expect(screen.getByText('Profile saved to the database.')).toBeInTheDocument()
    expect(screen.getByText(/New Person is now selected/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'View saved profile' })).toHaveAttribute('href', '/birth-profiles/7')
    expect(screen.getByRole('button', { name: 'Simulate create' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Simulate update' })).not.toBeInTheDocument()
  })
})

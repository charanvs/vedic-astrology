import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as api from '../../services/api'
import type { Location } from '../../types/api'
import { LocationForm } from './LocationForm'

const saved: Location = { id: 9, city: 'Sangrur', state: 'Punjab', country: 'India', country_code: 'IN', latitude: '30.2500000', longitude: '75.8400000', timezone: 'Asia/Kolkata', created_at: '2026-01-01T00:00:00' }

describe('LocationForm', () => {
  afterEach(() => vi.restoreAllMocks())

  it('saves independently without submitting its parent birth-profile form', async () => {
    const user = userEvent.setup()
    const outerSubmit = vi.fn((event: React.FormEvent) => event.preventDefault())
    const onCreated = vi.fn()
    vi.spyOn(api, 'createLocation').mockResolvedValue(saved)
    render(<form onSubmit={outerSubmit}><LocationForm initialCity="Sangrur" onCreated={onCreated} onCancel={vi.fn()} /></form>)
    await user.type(screen.getByLabelText('State or province'), 'Punjab')
    await user.type(screen.getByLabelText('Country'), 'India')
    await user.type(screen.getByLabelText('ISO country code'), 'IN')
    fireEvent.change(screen.getByLabelText('Latitude'), { target: { value: '30.25' } })
    fireEvent.change(screen.getByLabelText('Longitude'), { target: { value: '75.84' } })
    await user.type(screen.getByLabelText('IANA timezone'), 'Asia/Kolkata')
    await user.click(screen.getByRole('button', { name: 'Save verified location' }))
    await waitFor(() => expect(api.createLocation).toHaveBeenCalled())
    expect(onCreated).toHaveBeenCalledWith(saved)
    expect(outerSubmit).not.toHaveBeenCalled()
  })

  it('shows a flash error without submitting the parent when required data is absent', async () => {
    const user = userEvent.setup()
    const outerSubmit = vi.fn((event: React.FormEvent) => event.preventDefault())
    render(<form onSubmit={outerSubmit}><LocationForm onCreated={vi.fn()} onCancel={vi.fn()} /></form>)
    await user.click(screen.getByRole('button', { name: 'Save verified location' }))
    expect(screen.getByRole('alert')).toHaveTextContent(/Complete city, country, latitude, longitude/)
    expect(outerSubmit).not.toHaveBeenCalled()
  })
})

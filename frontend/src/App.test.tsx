import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import { ThemeProvider } from './hooks/useTheme'
import * as api from './services/api'

function renderApp(path = '/') {
  return render(<ThemeProvider><MemoryRouter initialEntries={[path]}><App /></MemoryRouter></ThemeProvider>)
}

describe('Step 4 portal experience', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getCurrentUser').mockResolvedValue({id:1,full_name:'Test User',email:'test@example.com',email_verified:true,approved:true,is_active:true,role:'user',created_at:'2026-01-01',last_login_at:null,deletion_requested_at:null})
    vi.spyOn(api, 'refreshCsrf').mockResolvedValue('csrf-test')
    vi.spyOn(api, 'getHealth').mockResolvedValue({ status: 'ok', application: 'vedic-astrology', service: 'backend' })
    vi.spyOn(api, 'getDatabaseHealth').mockResolvedValue({ status: 'ok', database: 'connected' })
    vi.spyOn(api, 'getBirthProfiles').mockResolvedValue([])
    vi.spyOn(api, 'getLocations').mockResolvedValue([])
  })
  afterEach(() => vi.restoreAllMocks())

  it('renders feature cards and actual service status', async () => {
    renderApp()
    expect(screen.getByRole('heading', { name: 'Welcome to Vedic Astrology' })).toBeInTheDocument()
    expect(screen.getAllByText('Daily Panchang')).toHaveLength(2)
    expect(screen.getAllByText('Kundli Matching')).toHaveLength(2)
    expect(await screen.findByText('Backend Connected')).toBeInTheDocument()
    expect(await screen.findByText('Database Connected')).toBeInTheDocument()
  })

  it('navigates to the refined Kundli form and highlights the active route', async () => {
    const user = userEvent.setup()
    renderApp()
    await user.click(screen.getByRole('link', { name: 'Create Birth Profile' }))
    expect(await screen.findByRole('heading', { name: 'North Indian Janam Kundli' })).toBeInTheDocument()
    expect(screen.getByLabelText('Full name')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Janam Kundli' })).toHaveClass('bg-[var(--primary-soft)]')
  })

  it('opens and closes the mobile navigation control', async () => {
    const user = userEvent.setup()
    renderApp()
    const open = screen.getByRole('button', { name: 'Open navigation' })
    expect(open).toHaveAttribute('aria-expanded', 'false')
    await user.click(open)
    expect(screen.getByRole('button', { name: 'Close navigation' })).toHaveAttribute('aria-expanded', 'true')
    await user.click(screen.getByRole('button', { name: 'Close navigation overlay' }))
    expect(screen.getByRole('button', { name: 'Open navigation' })).toBeInTheDocument()
  })

  it('persists light, dark and system theme choices', async () => {
    const user = userEvent.setup()
    renderApp()
    const theme = screen.getByRole('combobox', { name: 'Color theme' })
    await user.selectOptions(theme, 'dark')
    expect(document.documentElement).toHaveClass('dark')
    expect(localStorage.getItem('vedic-theme')).toBe('dark')
    await user.selectOptions(theme, 'system')
    expect(localStorage.getItem('vedic-theme')).toBe('system')
  })

  it('shows a real 404 page for unknown routes', () => {
    renderApp('/not-a-real-page')
    expect(screen.getByText(/404/)).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'This route is not in the chart' })).toBeInTheDocument()
  })
})

import { render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { BackendStatus } from './BackendStatus'
import * as api from '../../services/api'

describe('BackendStatus', () => {
  afterEach(() => vi.restoreAllMocks())
  it('renders connected after a successful check', async () => {
    vi.spyOn(api, 'getHealth').mockResolvedValue({ status: 'ok', application: 'vedic-astrology', service: 'backend' })
    vi.spyOn(api, 'getDatabaseHealth').mockResolvedValue({ status: 'ok', database: 'connected' })
    render(<BackendStatus />)
    expect(await screen.findByText('Backend Connected')).toBeInTheDocument()
  })
  it('renders unavailable after a failed check', async () => {
    vi.spyOn(api, 'getHealth').mockRejectedValue(new Error('offline'))
    vi.spyOn(api, 'getDatabaseHealth').mockRejectedValue(new Error('offline'))
    render(<BackendStatus />)
    expect(await screen.findByText('Backend Unavailable')).toBeInTheDocument()
  })
})

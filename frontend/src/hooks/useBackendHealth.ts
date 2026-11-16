import { useEffect, useState } from 'react'
import { getHealth } from '../services/api'
export type ConnectionState = 'loading' | 'connected' | 'unavailable'
export function useBackendHealth() {
  const [status, setStatus] = useState<ConnectionState>('loading')
  useEffect(() => { let active = true; getHealth().then((health) => { if (active) setStatus(health.status === 'ok' ? 'connected' : 'unavailable') }).catch(() => { if (active) setStatus('unavailable') }); return () => { active = false } }, [])
  return status
}

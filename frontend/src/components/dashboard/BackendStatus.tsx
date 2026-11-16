import { CheckCircle2, LoaderCircle, XCircle } from 'lucide-react'
import { useBackendHealth } from '../../hooks/useBackendHealth'
import { DatabaseStatus } from './DatabaseStatus'
export function BackendStatus() {
  const status = useBackendHealth()
  const content = { loading: { label: 'Checking backend…', detail: 'Confirming local API availability', Icon: LoaderCircle, style: 'text-slate-600 bg-slate-100', spin: true }, connected: { label: 'Backend Connected', detail: 'FastAPI service is responding normally', Icon: CheckCircle2, style: 'text-emerald-700 bg-emerald-50', spin: false }, unavailable: { label: 'Backend Unavailable', detail: 'Start FastAPI and refresh to reconnect', Icon: XCircle, style: 'text-rose-700 bg-rose-50', spin: false } }[status]
  return <><section aria-live="polite" className={`rounded-2xl p-5 ${content.style}`}><div className="flex items-center gap-3"><content.Icon className={`size-6 ${content.spin ? 'animate-spin' : ''}`} aria-hidden="true" /><div><p className="font-semibold">{content.label}</p><p className="text-sm opacity-80">{content.detail}</p></div></div></section><DatabaseStatus /></>
}

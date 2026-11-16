import { Download } from 'lucide-react'
import type { KundliDisplayMode } from './kundliTypes'

type Props = { mode: KundliDisplayMode; showHouseNumbers: boolean; onModeChange: (mode: KundliDisplayMode) => void; onHouseNumbersChange: (value: boolean) => void; onExport: () => void }

export function KundliControls({ mode, showHouseNumbers, onModeChange, onHouseNumbersChange, onExport }: Props) {
  return <div className="flex flex-wrap items-center gap-3" aria-label="Kundli display controls">
    <div className="inline-flex rounded-xl border border-[var(--border)] p-1" role="group" aria-label="Display detail">
      {(['standard', 'detailed'] as const).map((value) => <button key={value} type="button" aria-pressed={mode === value} onClick={() => onModeChange(value)} className={`min-h-10 rounded-lg px-3 text-sm font-semibold ${mode === value ? 'bg-[var(--primary-strong)] text-white' : 'text-[var(--muted)]'}`}>{value === 'standard' ? 'Standard' : 'Detailed'}</button>)}
    </div>
    <label className="flex min-h-11 items-center gap-2 rounded-xl border border-[var(--border)] px-3 text-sm font-semibold"><input type="checkbox" checked={showHouseNumbers} onChange={(event) => onHouseNumbersChange(event.target.checked)} className="size-4 accent-[var(--primary)]" />House numbers</label>
    <button type="button" onClick={onExport} className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-[var(--border)] px-3 text-sm font-bold"><Download className="size-4" />Export SVG</button>
  </div>
}

import type { AstrologyCalculation, DivisionalChart } from '../../types/api'

export function DivisionalDetails({ chart }: { chart: AstrologyCalculation | DivisionalChart }) {
  const divisional = 'chart_type' in chart
  return <dl className="grid grid-cols-2 gap-3 rounded-2xl bg-[var(--soft)] p-4 text-sm">
    <div><dt className="text-[var(--muted)]">Chart</dt><dd className="font-bold">{divisional ? `${chart.chart_type} ${chart.chart_name}` : 'D1 Rashi'}</dd></div>
    <div><dt className="text-[var(--muted)]">Lagna</dt><dd className="font-bold">{chart.lagna.rashi.name}</dd></div>
    <div><dt className="text-[var(--muted)]">System</dt><dd className="font-semibold">{divisional ? chart.calculation.system : 'Birth chart'}</dd></div>
    <div><dt className="text-[var(--muted)]">Houses</dt><dd className="font-semibold">Whole sign</dd></div>
    <div><dt className="text-[var(--muted)]">Ayanamsa</dt><dd className="font-semibold">Lahiri</dd></div>
    <div><dt className="text-[var(--muted)]">Node</dt><dd className="font-semibold">Mean</dd></div>
  </dl>
}

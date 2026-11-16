import type { AstrologyCalculation, DivisionalChart } from '../../types/api'

export function DivisionalPlanetTable({ chart }: { chart: AstrologyCalculation | DivisionalChart }) {
  const divisional = 'chart_type' in chart
  return <div className="overflow-x-auto rounded-2xl border border-[var(--border)]"><table className="w-full min-w-[760px] text-left text-sm">
    <caption className="sr-only">{divisional ? chart.chart_type : 'D1'} planetary positions</caption>
    <thead className="bg-[var(--soft)]"><tr>{['Graha', ...(divisional ? ['D1 Rashi', 'Division'] : []), 'Chart Rashi', 'Degree', 'House', ...(divisional && chart.chart_type === 'D9' ? ['Vargottama'] : []), 'Motion'].map(label => <th key={label} className="px-3 py-3">{label}</th>)}</tr></thead>
    <tbody>{chart.planets.map(planet => { const item = divisional ? planet as DivisionalChart['planets'][number] : undefined; return <tr key={planet.identifier} className="border-t border-[var(--border)]">
      <td className="px-3 py-3 font-bold">{planet.english_name}<span className="block text-xs font-normal text-[var(--muted)]">{planet.sanskrit_name}</span></td>
      {item && <><td className="px-3 py-3">{item.original_rashi.name}</td><td className="px-3 py-3 tabular-nums">{item.division_number}</td></>}
      <td className="px-3 py-3">{planet.rashi.name}</td><td className="px-3 py-3 tabular-nums">{planet.rashi.longitude_within.toFixed(6)}°</td><td className="px-3 py-3">{planet.house}</td>
      {item && 'chart_type' in chart && chart.chart_type === 'D9' && <td className="px-3 py-3">{item.vargottama ? 'Yes' : '—'}</td>}
      <td className="px-3 py-3 capitalize">{planet.motion}{planet.retrograde ? ' (R)' : ''}</td>
    </tr>})}</tbody>
  </table></div>
}

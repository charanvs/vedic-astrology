import { CalendarDays, CircleDashed, Moon, Sparkles, Star } from 'lucide-react'
import { useState, type ReactNode } from 'react'
import type { PanchangResult } from '../../types/api'
import { AppCard } from '../common/AppCard'
import { PanchangDetails, type PanchangElementKey } from './PanchangDetails'
import { PanchangElementCard } from './PanchangElementCard'
import { PanchangTimeline } from './PanchangTimeline'
import { formatLocalDateTime } from './panchangFormat'
import { SunriseSunsetPanel } from './SunriseSunsetPanel'

type CardDefinition = [
  PanchangElementKey,
  string,
  string,
  string | undefined,
  string | undefined,
  ReactNode,
]

export function PanchangDashboard({ result }: { result: PanchangResult }) {
  const [selected, setSelected] = useState<PanchangElementKey>('tithi')
  const zone = result.location.timezone
  const end = (value: string) =>
    formatLocalDateTime(value, zone, value.slice(0, 10) !== result.civil_date)
  const cards: CardDefinition[] = [
    [
      'tithi',
      'Tithi',
      result.tithi.display_name,
      result.tithi.paksha,
      end(result.tithi.end.local),
      <Moon key="tithi-icon" className="size-4" />,
    ],
    [
      'vara',
      'Vara',
      result.vara.name,
      result.vara.english_name,
      undefined,
      <CalendarDays key="vara-icon" className="size-4" />,
    ],
    [
      'nakshatra',
      'Nakshatra',
      result.nakshatra.name,
      `Pada ${result.nakshatra.pada} · ${result.nakshatra.lord}`,
      end(result.nakshatra.end.local),
      <Star key="nakshatra-icon" className="size-4" />,
    ],
    [
      'yoga',
      'Yoga',
      result.yoga.name,
      undefined,
      end(result.yoga.end.local),
      <Sparkles key="yoga-icon" className="size-4" />,
    ],
    [
      'karana',
      'Karana',
      result.karana.name,
      `${result.karana.half} half of Tithi ${result.karana.tithi_number}`,
      end(result.karana.end.local),
      <CircleDashed key="karana-icon" className="size-4" />,
    ],
  ]

  return (
    <div className="space-y-6">
      <SunriseSunsetPanel result={result} />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        {cards.map(([key, label, name, secondary, ending, icon]) => (
          <PanchangElementCard
            key={key}
            label={label}
            name={name}
            secondary={secondary}
            end={ending}
            next={key === 'vara' ? undefined : result[key].next.name}
            selected={selected === key}
            icon={icon}
            onSelect={() => setSelected(key)}
          />
        ))}
      </div>
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(280px,420px)]">
        <AppCard className="p-5 sm:p-6">
          <PanchangTimeline result={result} />
        </AppCard>
        <PanchangDetails result={result} selected={selected} />
      </div>
      <AppCard className="p-5">
        <dl className="grid gap-4 text-sm sm:grid-cols-2 lg:grid-cols-4">
          <div><dt className="text-[var(--muted)]">Method</dt><dd className="font-bold">{String(result.settings.method)}</dd></div>
          <div><dt className="text-[var(--muted)]">Ayanamsa</dt><dd className="font-bold">{String(result.settings.ayanamsa)}</dd></div>
          <div><dt className="text-[var(--muted)]">Panchang day</dt><dd className="font-bold">Sunrise to next sunrise</dd></div>
          <div><dt className="text-[var(--muted)]">Engine</dt><dd className="font-bold">{String(result.engine.engine)}</dd></div>
        </dl>
      </AppCard>
    </div>
  )
}

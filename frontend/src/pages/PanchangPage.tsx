import { useEffect, useMemo, useState } from 'react'
import { AppCard } from '../components/common/AppCard'
import { PageHeader } from '../components/common/PageHeader'
import { PanchangDashboard } from '../components/panchang/PanchangDashboard'
import { PanchangDateSelector } from '../components/panchang/PanchangDateSelector'
import { PanchangError } from '../components/panchang/PanchangError'
import { PanchangLoading } from '../components/panchang/PanchangLoading'
import { PanchangLocationSelector } from '../components/panchang/PanchangLocationSelector'
import { locationToday } from '../components/panchang/panchangFormat'
import { panchangText } from '../constants/panchangText'
import { apiErrorMessage, getDailyPanchang, getLocations } from '../services/api'
import type { Location, PanchangResult } from '../types/api'

export function PanchangPage() {
  const [locations, setLocations] = useState<Location[]>([])
  const [selected, setSelected] = useState<Location>()
  const [date, setDate] = useState(locationToday('UTC'))
  const [result, setResult] = useState<PanchangResult>()
  const [loadingLocations, setLoadingLocations] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [retry, setRetry] = useState(0)

  useEffect(() => {
    getLocations()
      .then((items) => {
        setLocations(items)
        if (items[0]) {
          setSelected(items[0])
          setDate(locationToday(items[0].timezone))
        }
      })
      .catch((reason) => setError(apiErrorMessage(reason, 'Stored locations could not be loaded.')))
      .finally(() => setLoadingLocations(false))
  }, [])

  useEffect(() => {
    if (!selected || !date) return
    const controller = new AbortController()
    // Loading and errors intentionally reset when a new external request begins.
    // oxlint-disable-next-line react/set-state-in-effect
    setLoading(true)
    setError('')
    getDailyPanchang(date, selected.id, controller.signal)
      .then(setResult)
      .catch((reason) => {
        const message = apiErrorMessage(reason, 'Daily Panchang could not be calculated.')
        if (message) setError(message)
      })
      .finally(() => setLoading(false))
    return () => controller.abort()
  }, [selected, date, retry])

  const today = useMemo(() => locationToday(selected?.timezone ?? 'UTC'), [selected])
  return (
    <div className="min-w-0 space-y-6">
      <PageHeader title={panchangText.title} description={panchangText.subtitle} />
      <AppCard className="grid min-w-0 gap-5 p-5 lg:grid-cols-2">
        <PanchangLocationSelector
          locations={locations}
          value={selected?.id ?? null}
          onChange={(location) => {
            setSelected(location)
            setResult(undefined)
            if (location) setDate(locationToday(location.timezone))
          }}
        />
        <PanchangDateSelector value={date} today={today} onChange={setDate} />
        {selected && (
          <p className="break-words text-sm text-[var(--muted)] lg:col-span-2">
            Coordinates {selected.latitude}, {selected.longitude} · Timezone {selected.timezone}
          </p>
        )}
      </AppCard>
      {loadingLocations ? (
        <PanchangLoading />
      ) : locations.length === 0 ? (
        <p className="rounded-2xl bg-[var(--soft)] p-5 text-[var(--muted)]">{panchangText.noLocations}</p>
      ) : !selected ? (
        <p className="rounded-2xl bg-[var(--soft)] p-5 text-[var(--muted)]">{panchangText.emptyLocation}</p>
      ) : loading ? (
        <PanchangLoading />
      ) : error ? (
        <PanchangError message={error} onRetry={() => setRetry((value) => value + 1)} />
      ) : result ? (
        <PanchangDashboard result={result} />
      ) : null}
    </div>
  )
}

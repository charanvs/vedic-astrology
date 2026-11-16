import { useEffect, useState } from 'react'
import { AppCard } from '../components/common/AppCard'
import { PageHeader } from '../components/common/PageHeader'
import { useAuth } from '../hooks/useAuth'
import { useTheme, type Theme } from '../hooks/useTheme'
import { apiErrorMessage, getMatchingConfig } from '../services/api'
import type { DashaYearConvention, MatchingConfig, ReportLanguage } from '../types/api'

const themes: Array<{ value: Theme; label: string }> = [{ value: 'light', label: 'Light' }, { value: 'dark', label: 'Dark' }, { value: 'system', label: 'Match system' }]
const languages: Array<{ value: ReportLanguage; label: string }> = [{ value: 'en', label: 'English' }, { value: 'hi', label: 'हिन्दी' }, { value: 'pa', label: 'ਪੰਜਾਬੀ' }]
const conventions: Array<{ value: DashaYearConvention; label: string }> = [{ value: '365.25_day', label: '365.25-day year' }, { value: '360_day_savana', label: '360-day Savana year' }]

export function SettingsPage() {
  const { preferences, updatePreferences } = useAuth()
  const { theme, setTheme } = useTheme()
  const [matchingConfig, setMatchingConfig] = useState<MatchingConfig>()
  const [message, setMessage] = useState('')
  useEffect(() => { getMatchingConfig().then(setMatchingConfig).catch(() => undefined) }, [])

  async function changeTheme(value: Theme) {
    setTheme(value)
    try { await updatePreferences({ theme: value }) } catch (error) { setMessage(apiErrorMessage(error, 'Theme preference could not be saved.')) }
  }
  async function changeLanguage(value: ReportLanguage) {
    localStorage.setItem('report-language', value)
    try { await updatePreferences({ report_language: value }); setMessage('Default report language saved.') } catch (error) { setMessage(apiErrorMessage(error, 'Report language preference could not be saved.')) }
  }
  async function changeConvention(value: DashaYearConvention) {
    localStorage.setItem('dasha-year-convention', value)
    try { await updatePreferences({ dasha_year_convention: value }); setMessage('Default Dasha year convention saved.') } catch (error) { setMessage(apiErrorMessage(error, 'Dasha year convention preference could not be saved.')) }
  }

  const effectiveLanguage = preferences?.report_language || (localStorage.getItem('report-language') as ReportLanguage) || 'en'
  const effectiveConvention = preferences?.dasha_year_convention || (localStorage.getItem('dasha-year-convention') as DashaYearConvention) || '365.25_day'
  const ruleset = matchingConfig?.supported_rulesets[0]

  return <div className="space-y-6">
    <PageHeader title="Settings" description="Preferences that apply across the application for your account." />
    {message && <p role="status" className="rounded-xl bg-[var(--primary-soft)] p-3 text-sm">{message}</p>}
    <AppCard className="space-y-3 p-5 sm:p-6">
      <h2 className="text-xl font-bold">Appearance</h2>
      <p className="text-sm text-[var(--muted)]">Choose how the application looks. This is remembered on your account and applied wherever you sign in.</p>
      <div className="flex flex-wrap gap-3" role="group" aria-label="Theme">
        {themes.map(item => <button key={item.value} type="button" aria-pressed={theme === item.value} onClick={() => void changeTheme(item.value)} className={`min-h-11 rounded-xl border border-[var(--border)] px-4 font-bold ${theme === item.value ? 'bg-[var(--primary-strong)] text-white' : 'bg-[var(--surface)]'}`}>{item.label}</button>)}
      </div>
    </AppCard>
    <AppCard className="space-y-3 p-5 sm:p-6">
      <h2 className="text-xl font-bold">Default report language</h2>
      <p className="text-sm text-[var(--muted)]">Pre-selects the language whenever you open PDF Reports. You can still change it per report.</p>
      <label className="block max-w-xs font-bold">Language<select aria-label="Default report language" value={effectiveLanguage} onChange={e => void changeLanguage(e.target.value as ReportLanguage)} className="mt-2 min-h-11 w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3">{languages.map(item => <option key={item.value} value={item.value}>{item.label}</option>)}</select></label>
    </AppCard>
    <AppCard className="space-y-3 p-5 sm:p-6">
      <h2 className="text-xl font-bold">Default Dasha year convention</h2>
      <p className="text-sm text-[var(--muted)]">Pre-selects the year convention whenever you open Dasha Analysis. You can still change it per calculation.</p>
      <label className="block max-w-xs font-bold">Year convention<select aria-label="Default Dasha year convention" value={effectiveConvention} onChange={e => void changeConvention(e.target.value as DashaYearConvention)} className="mt-2 min-h-11 w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3">{conventions.map(item => <option key={item.value} value={item.value}>{item.label}</option>)}</select></label>
    </AppCard>
    <AppCard className="space-y-2 p-5 sm:p-6">
      <h2 className="text-xl font-bold">Matching ruleset</h2>
      <p className="text-sm text-[var(--muted)]">{ruleset ? `Only one Ashtakoota ruleset is currently available (${ruleset.name}, ${ruleset.version}). It is used for every match automatically; there is nothing to choose yet.` : 'Loading ruleset information…'}</p>
    </AppCard>
  </div>
}

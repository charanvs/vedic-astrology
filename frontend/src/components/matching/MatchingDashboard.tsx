import type { MatchingResult } from '../../types/api'
import { matchingText } from '../../constants/matchingText'
import { ComparisonDetails } from './ComparisonDetails'
import { DoshaObservations } from './DoshaObservations'
import { KootaBreakdownTable } from './KootaBreakdownTable'
import { MatchingSummary } from './MatchingSummary'

export function MatchingDashboard({result}:{result:MatchingResult}){return <div className="space-y-6" aria-live="polite"><MatchingSummary result={result}/><KootaBreakdownTable result={result}/><DoshaObservations result={result}/><ComparisonDetails result={result}/><section className="rounded-2xl bg-[var(--soft)] p-5 text-sm leading-6 text-[var(--muted)]"><h2 className="font-bold text-[var(--text)]">About this traditional score</h2><p className="mt-2">{matchingText.disclaimer}</p><p className="mt-2">A commonly used 18-point threshold is presentation context, not a marriage recommendation or verdict. Regional tables differ, and this result uses only the named ruleset.</p></section></div>}

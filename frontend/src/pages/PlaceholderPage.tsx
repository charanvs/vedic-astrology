import { Construction, type LucideIcon } from 'lucide-react'
import { AppCard } from '../components/common/AppCard'

export function PlaceholderPage({ title, icon: Icon }: { title: string; icon: LucideIcon }) {
  return <AppCard className="mx-auto max-w-4xl p-8 text-center sm:p-14">
    <div className="mx-auto grid size-16 place-items-center rounded-2xl bg-[var(--primary-soft)] text-[var(--primary-strong)]"><Icon className="size-8" aria-hidden="true" /></div>
    <p className="mt-6 text-sm font-bold uppercase tracking-widest text-[var(--primary-strong)]">Under Development</p>
    <h1 className="mt-2 text-3xl font-bold">{title}</h1>
    <p className="mx-auto mt-4 max-w-xl leading-7 text-[var(--muted)]">This module is planned for a later milestone. No astrological data or calculations are generated in this foundation release.</p>
    <Construction className="mx-auto mt-8 text-[var(--muted)]" aria-hidden="true" />
  </AppCard>
}

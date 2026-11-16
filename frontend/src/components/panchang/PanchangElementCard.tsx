import type { ReactNode } from 'react'

type PanchangElementCardProps = {
  label: string
  name: string
  secondary?: string
  end?: string
  next?: string
  selected: boolean
  icon: ReactNode
  onSelect: () => void
}

export function PanchangElementCard({
  label,
  name,
  secondary,
  end,
  next,
  selected,
  icon,
  onSelect,
}: PanchangElementCardProps) {
  return (
    <button
      type="button"
      aria-label={`${label}: ${name}`}
      aria-pressed={selected}
      onClick={onSelect}
      className={`min-h-48 rounded-2xl border p-5 text-left shadow-sm transition ${
        selected
          ? 'border-[var(--primary)] bg-[var(--primary-soft)]'
          : 'border-[var(--border)] bg-[var(--surface)] hover:border-[var(--primary)]'
      }`}
    >
      <span className="flex items-center gap-2 text-sm font-bold uppercase tracking-wide text-[var(--primary-strong)]">
        {icon}
        {label}
      </span>
      <strong className="mt-4 block text-2xl">{name}</strong>
      {secondary && <span className="mt-1 block text-sm text-[var(--muted)]">{secondary}</span>}
      {end && (
        <span className="mt-5 block text-sm">
          <span className="text-[var(--muted)]">Ends</span>
          <br />
          <strong>{end}</strong>
        </span>
      )}
      {next && (
        <span className="mt-3 block text-sm">
          <span className="text-[var(--muted)]">Next</span> · {next}
        </span>
      )}
    </button>
  )
}

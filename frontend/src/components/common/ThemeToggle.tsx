import { MonitorCog } from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'
import { useTheme } from '../../hooks/useTheme'
import type { Theme } from '../../hooks/useTheme'

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const { user, updatePreferences } = useAuth()
  function change(value: Theme) {
    setTheme(value)
    if (user) void updatePreferences({ theme: value }).catch(() => undefined)
  }
  return <label className="flex min-h-10 items-center gap-2 rounded-xl border border-[var(--border)] px-2 text-[var(--muted)] hover:bg-[var(--soft)]">
    <MonitorCog className="size-4" aria-hidden="true" />
    <span className="sr-only">Color theme</span>
    <select aria-label="Color theme" value={theme} onChange={(event) => change(event.target.value as Theme)} className="max-w-20 bg-transparent text-xs font-semibold text-[var(--text)] outline-none sm:max-w-none">
      <option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option>
    </select>
  </label>
}

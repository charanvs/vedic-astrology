import { Menu, MoonStar, Settings, ShieldCheck, X } from 'lucide-react'
import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { ThemeToggle } from '../components/common/ThemeToggle'
import { uiText } from '../constants/ui'
import { routeItems } from '../routes/navigation'
import {useAuth} from '../hooks/useAuth'

const navLinkClass = ({ isActive }: { isActive: boolean }) => `flex min-h-11 items-center gap-3 rounded-xl px-3 py-2 text-sm font-semibold transition ${isActive ? 'bg-[var(--primary-soft)] text-[var(--primary-strong)]' : 'text-[var(--muted)] hover:bg-[var(--soft)] hover:text-[var(--text)]'}`

export function PortalLayout() {
  const [open, setOpen] = useState(false)
  const {user,logout}=useAuth()
  return <div className="min-h-screen bg-[var(--background)] text-[var(--text)]">
    <header className="sticky top-0 z-40 border-b border-[var(--border)] bg-[var(--surface-translucent)] backdrop-blur-xl"><div className="flex h-20 items-center gap-3 px-4 sm:px-6">
      <button type="button" aria-label={open ? 'Close navigation' : 'Open navigation'} aria-expanded={open} className="grid size-10 shrink-0 place-items-center rounded-xl border border-[var(--border)] lg:hidden" onClick={() => setOpen((value) => !value)}>{open ? <X /> : <Menu />}</button>
      <div className="grid size-11 shrink-0 place-items-center rounded-2xl bg-[var(--primary)] text-white"><MoonStar /></div>
      <div className="min-w-0"><p className="truncate text-lg font-bold">{uiText.appName}</p><p className="hidden truncate text-xs text-[var(--muted)] sm:block sm:text-sm">{uiText.subtitle}</p></div>
      <div className="ml-auto flex shrink-0 items-center gap-2"><div className="hidden sm:block"><ThemeToggle /></div>{user?<><NavLink to="/account" className="rounded-xl border border-[var(--border)] px-3 py-2 text-sm">{user.full_name}</NavLink><button onClick={()=>void logout()} className="rounded-xl border border-[var(--border)] px-3 py-2 text-sm">Sign out</button></>:<NavLink to="/login" className="rounded-xl bg-[var(--primary)] px-3 py-2 text-sm text-white">Sign in</NavLink>}<NavLink to="/settings" aria-label="Settings" className="hidden size-10 place-items-center rounded-xl border border-[var(--border)] text-[var(--muted)] hover:bg-[var(--soft)] sm:grid"><Settings className="size-5" /></NavLink></div>
    </div></header>
    <div className="flex">
      {open && <button aria-label="Close navigation overlay" className="fixed inset-0 top-20 z-20 bg-black/40 lg:hidden" onClick={() => setOpen(false)} />}
      <aside className={`${open ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-20 left-0 z-30 flex w-72 flex-col border-r border-[var(--border)] bg-[var(--surface)] p-4 transition-transform lg:sticky lg:top-20 lg:h-[calc(100vh-5rem)] lg:translate-x-0`}>
        <nav aria-label="Primary navigation" className="space-y-1">{routeItems.map(({ label, path, icon: Icon }) => <NavLink key={path} to={path} end={path === '/'} onClick={() => setOpen(false)} className={navLinkClass}><Icon className="size-5" />{label}</NavLink>)}{user?.role === 'admin' && <NavLink to="/admin" onClick={() => setOpen(false)} className={navLinkClass}><ShieldCheck className="size-5" />Administration</NavLink>}</nav>
        <div className="mt-auto rounded-2xl bg-[var(--soft)] p-4 text-xs leading-5 text-[var(--muted)]"><strong className="text-[var(--text)]">{user?'Private account':'Guest access'}</strong><br />{user?'Saved profiles are scoped to your authenticated account.':'Sign in to manage private profiles and reports.'}</div>
      </aside>
      <div className="min-w-0 flex-1"><main className="mx-auto min-h-[calc(100vh-9rem)] max-w-[1600px] p-4 sm:p-6 lg:p-8"><Outlet /></main><footer className="border-t border-[var(--border)] px-6 py-5 text-center text-xs leading-6 text-[var(--muted)]">Vedic Astrology · Version 1.2.0 · Free software under the <a className="underline" href="https://www.gnu.org/licenses/agpl-3.0.html" rel="license noreferrer" target="_blank">GNU AGPL v3</a> · <a className="underline" href={`${import.meta.env.BASE_URL}api/source`} target="_blank" rel="noreferrer">Source code</a> · Astronomy by <a className="underline" href="https://www.astro.com/swisseph/" target="_blank" rel="noreferrer">Swiss Ephemeris</a> · City data © <a className="underline" href="https://www.geonames.org/" target="_blank" rel="noreferrer">GeoNames</a> (<a className="underline" href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noreferrer">CC BY 4.0</a>)</footer></div>
    </div>
  </div>
}

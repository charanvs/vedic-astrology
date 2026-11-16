import { ArrowLeft, Compass } from 'lucide-react'
import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return <div className="grid min-h-[60vh] place-items-center text-center"><div>
    <Compass className="mx-auto size-14 text-[var(--primary)]" />
    <p className="mt-5 text-sm font-bold uppercase tracking-widest text-[var(--primary)]">404 · Page not found</p>
    <h1 className="mt-2 text-3xl font-bold">This route is not in the chart</h1>
    <p className="mt-3 text-[var(--muted)]">Return to the dashboard and choose an available module.</p>
    <Link to="/" className="mt-6 inline-flex items-center gap-2 rounded-xl bg-[var(--primary)] px-5 py-3 font-bold text-white"><ArrowLeft className="size-4" />Dashboard</Link>
  </div></div>
}

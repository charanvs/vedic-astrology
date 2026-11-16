import { BookOpenText, CircleDot, FileDown, Gauge, HeartHandshake, Layers3, Orbit, Save, Settings, SunMedium, type LucideIcon } from 'lucide-react'
export type RouteItem = { label: string; path: string; icon: LucideIcon; description: string }
export const routeItems: RouteItem[] = [
  { label: 'Dashboard', path: '/', icon: Gauge, description: 'Application overview and service status' },
  { label: 'Janam Kundli', path: '/kundli', icon: CircleDot, description: 'Create birth profiles and view a North Indian chart' },
  { label: 'Planetary Positions', path: '/planets', icon: Orbit, description: 'Review sidereal planetary placements' },
  { label: 'Daily Panchang', path: '/panchang', icon: SunMedium, description: 'Explore the daily Hindu almanac' },
  { label: 'Dasha Analysis', path: '/dasha', icon: BookOpenText, description: 'Study Vimshottari dasha periods' },
  { label: 'Kundli Matching', path: '/matching', icon: HeartHandshake, description: 'Compare two birth charts' },
  { label: 'Divisional Charts', path: '/divisional-charts', icon: Layers3, description: 'Explore Navamsha and Dashamsha charts' },
  { label: 'PDF Reports', path: '/reports', icon: FileDown, description: 'Generate multilingual Kundli PDF reports' },
  { label: 'Saved Profiles', path: '/saved-charts', icon: Save, description: 'Review stored birth profiles' },
  { label: 'Settings', path: '/settings', icon: Settings, description: 'Manage application preferences' },
]

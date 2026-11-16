import { Route, Routes } from 'react-router-dom'
import type {ReactNode} from 'react'
import { PortalLayout } from './layouts/PortalLayout'
import { DashboardPage as HomePage } from './pages/DashboardPage'
import { PlaceholderPage } from './pages/PlaceholderPage'
import { KundliPage } from './pages/KundliPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { SavedProfilesPage } from './pages/SavedProfilesPage'
import { BirthProfileDetailsPage } from './pages/BirthProfileDetailsPage'
import { PlanetaryPositionsPage } from './pages/PlanetaryPositionsPage'
import { PanchangPage } from './pages/PanchangPage'
import { DashaPage } from './pages/DashaPage'
import { MatchingPage } from './pages/MatchingPage'
import { DivisionalChartsPage } from './pages/DivisionalChartsPage'
import { ReportsPage } from './pages/ReportsPage'
import { routeItems } from './routes/navigation'
import {AuthProvider} from './hooks/useAuth'
import {ProtectedRoute} from './components/common/ProtectedRoute'
import {ForgotPasswordPage,LoginPage,RegisterPage,ResetPasswordPage,VerifyEmailPage} from './pages/AuthPages'
import {AccountPage} from './pages/AccountPage'
import {SettingsPage} from './pages/SettingsPage'
import {AdminPage} from './pages/AdminPage'

export default function App() {
  const protect=(node:ReactNode)=><ProtectedRoute>{node}</ProtectedRoute>
  return <AuthProvider><Routes><Route element={<PortalLayout />}><Route index element={<HomePage />} /><Route path="/login" element={<LoginPage/>}/><Route path="/register" element={<RegisterPage/>}/><Route path="/forgot-password" element={<ForgotPasswordPage/>}/><Route path="/reset-password" element={<ResetPasswordPage/>}/><Route path="/verify-email" element={<VerifyEmailPage/>}/><Route path="/account" element={protect(<AccountPage/>)}/><Route path="/kundli" element={protect(<KundliPage />)}/><Route path="/birth-profiles/:id/edit" element={protect(<KundliPage/>)}/><Route path="/birth-profiles/:id" element={protect(<BirthProfileDetailsPage/>)}/><Route path="/saved-charts" element={protect(<SavedProfilesPage/>)}/><Route path="/planets" element={protect(<PlanetaryPositionsPage/>)}/><Route path="/panchang" element={<PanchangPage/>}/><Route path="/dasha" element={protect(<DashaPage/>)}/><Route path="/matching" element={protect(<MatchingPage/>)}/><Route path="/divisional-charts" element={protect(<DivisionalChartsPage/>)}/><Route path="/reports" element={protect(<ReportsPage/>)}/><Route path="/settings" element={protect(<SettingsPage/>)}/><Route path="/admin" element={protect(<AdminPage/>)}/>{routeItems.filter((item) => !['/','/kundli','/saved-charts','/planets','/panchang','/dasha','/matching','/divisional-charts','/reports','/settings'].includes(item.path)).map((item) => <Route key={item.path} path={item.path} element={<PlaceholderPage title={item.label} icon={item.icon} />} />)}<Route path="*" element={<NotFoundPage/>}/></Route></Routes></AuthProvider>
}

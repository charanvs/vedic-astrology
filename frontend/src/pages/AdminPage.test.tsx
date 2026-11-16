import {render,screen,waitFor,within} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import {MemoryRouter} from 'react-router-dom'
import {afterEach,describe,expect,it,vi} from 'vitest'
import App from '../App'
import {ThemeProvider} from '../hooks/useTheme'
import * as api from '../services/api'

const base={email_verified:true,approved:true,is_active:true,created_at:'2026-01-01',last_login_at:null,deletion_requested_at:null}
const admin={id:1,full_name:'Site Admin',email:'admin@example.com',role:'admin' as const,...base}
const member={id:2,full_name:'Plain Member',email:'member@example.com',role:'user' as const,...base}
const pending:api.AdminUser={id:7,full_name:'New Applicant',email:'applicant@example.com',role:'user',status:'pending',email_verified:false,approved_at:null,created_at:'2026-11-16T08:00:00',last_login_at:null,deletion_requested_at:null,profile_count:0}
function signedInAs(user:typeof admin|typeof member){vi.spyOn(api,'getCurrentUser').mockResolvedValue(user);vi.spyOn(api,'refreshCsrf').mockResolvedValue('csrf');vi.spyOn(api,'getPreferences').mockResolvedValue({theme:null,report_language:null,dasha_year_convention:null,matching_ruleset:null})}
function renderAt(path:string){return render(<ThemeProvider><MemoryRouter initialEntries={[path]}><App/></MemoryRouter></ThemeProvider>)}
afterEach(()=>vi.restoreAllMocks())

describe('Admin page',()=>{
 it('lists pending registrations and approves one',async()=>{
  signedInAs(admin)
  vi.spyOn(api,'getAdminSummary').mockResolvedValueOnce({pending:1,approved:1,inactive:0,all:2}).mockResolvedValue({pending:0,approved:2,inactive:0,all:2})
  vi.spyOn(api,'listAdminUsers').mockResolvedValueOnce([pending]).mockResolvedValue([])
  const change=vi.spyOn(api,'changeUserStatus').mockResolvedValue({...pending,status:'approved'})
  const user=userEvent.setup()
  renderAt('/admin')
  expect(await screen.findByText('New Applicant',{selector:'strong'})).toBeInTheDocument()
  expect(within(screen.getByRole('group',{name:'Filter users by status'})).getByRole('button',{name:'Pending approval (1)'})).toHaveAttribute('aria-pressed','true')
  expect(screen.getByRole('link',{name:'Administration'})).toBeInTheDocument()
  await user.click(within(screen.getByRole('list',{name:'Users'})).getByRole('button',{name:'Approve New Applicant'}))
  expect(change).toHaveBeenCalledWith(7,'approve')
  expect(await screen.findByText('New Applicant is now approved.')).toBeInTheDocument()
  expect(await screen.findByText('No registrations are waiting for approval.')).toBeInTheDocument()
 })

 it('asks for confirmation before deactivating',async()=>{
  signedInAs(admin)
  vi.spyOn(api,'getAdminSummary').mockResolvedValue({pending:1,approved:1,inactive:0,all:2})
  vi.spyOn(api,'listAdminUsers').mockResolvedValue([pending])
  const change=vi.spyOn(api,'changeUserStatus')
  vi.spyOn(window,'confirm').mockReturnValue(false)
  const user=userEvent.setup()
  renderAt('/admin')
  await screen.findByText('New Applicant',{selector:'strong'})
  await user.click(within(screen.getByRole('list',{name:'Users'})).getByRole('button',{name:'Deactivate New Applicant'}))
  expect(window.confirm).toHaveBeenCalled()
  expect(change).not.toHaveBeenCalled()
 })

 it('denies regular users and hides the administration link',async()=>{
  signedInAs(member)
  const list=vi.spyOn(api,'listAdminUsers')
  renderAt('/admin')
  expect(await screen.findByRole('heading',{name:'Administrator access required'})).toBeInTheDocument()
  expect(screen.queryByRole('link',{name:'Administration'})).not.toBeInTheDocument()
  await waitFor(()=>expect(list).not.toHaveBeenCalled())
 })
})

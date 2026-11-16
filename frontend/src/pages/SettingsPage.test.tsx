import {render,screen} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import {MemoryRouter} from 'react-router-dom'
import {afterEach,describe,expect,it,vi} from 'vitest'
import App from '../App'
import {ThemeProvider} from '../hooks/useTheme'
import * as api from '../services/api'
const user={id:1,full_name:'Pref User',email:'pref@example.com',email_verified:true,approved:true,is_active:true,role:'user' as const,created_at:'2026-01-01',last_login_at:null,deletion_requested_at:null}
function renderApp(path:string){return render(<ThemeProvider><MemoryRouter initialEntries={[path]}><App/></MemoryRouter></ThemeProvider>)}
afterEach(()=>{vi.restoreAllMocks();localStorage.clear()})
describe('Settings page',()=>{
 it('shows saved preference defaults and lets the user change the theme',async()=>{
  vi.spyOn(api,'getCurrentUser').mockResolvedValue(user)
  vi.spyOn(api,'refreshCsrf').mockResolvedValue('csrf-token')
  vi.spyOn(api,'getPreferences').mockResolvedValue({theme:'dark',report_language:'hi',dasha_year_convention:'360_day_savana',matching_ruleset:'muhurta_chintamani_joshi_v1'})
  vi.spyOn(api,'getMatchingConfig').mockResolvedValue({supported_rulesets:[{id:'muhurta_chintamani_joshi_v1',name:'Muhurta Chintamani (Joshi)',version:'v1'}],default_ruleset:'muhurta_chintamani_joshi_v1',koota_maximums:{},total_maximum:'36',roles:['bride','groom'],engine:{},ayanamsa:'Lahiri',public_deployment_blocked:false})
  const update=vi.spyOn(api,'updatePreferences').mockResolvedValue({theme:'light',report_language:'hi',dasha_year_convention:'360_day_savana',matching_ruleset:'muhurta_chintamani_joshi_v1'})
  const actor=userEvent.setup()
  renderApp('/settings')
  expect(await screen.findByRole('heading',{name:'Settings'})).toBeInTheDocument()
  expect(await screen.findByText(/Muhurta Chintamani \(Joshi\), v1/)).toBeInTheDocument()
  const languageSelect=await screen.findByLabelText('Default report language') as HTMLSelectElement
  expect(languageSelect.value).toBe('hi')
  const lightButton=screen.getByRole('button',{name:'Light'})
  await actor.click(lightButton)
  expect(update).toHaveBeenCalledWith({theme:'light'})
  expect(lightButton).toHaveAttribute('aria-pressed','true')
 })
 it('persists the default report language to localStorage for the Reports page to read',async()=>{
  vi.spyOn(api,'getCurrentUser').mockResolvedValue(user)
  vi.spyOn(api,'refreshCsrf').mockResolvedValue('csrf-token')
  vi.spyOn(api,'getPreferences').mockResolvedValue({theme:null,report_language:null,dasha_year_convention:null,matching_ruleset:null})
  vi.spyOn(api,'getMatchingConfig').mockResolvedValue({supported_rulesets:[{id:'muhurta_chintamani_joshi_v1',name:'Muhurta Chintamani (Joshi)',version:'v1'}],default_ruleset:'muhurta_chintamani_joshi_v1',koota_maximums:{},total_maximum:'36',roles:['bride','groom'],engine:{},ayanamsa:'Lahiri',public_deployment_blocked:false})
  vi.spyOn(api,'updatePreferences').mockResolvedValue({theme:null,report_language:'pa',dasha_year_convention:null,matching_ruleset:null})
  const actor=userEvent.setup()
  renderApp('/settings')
  const languageSelect=await screen.findByLabelText('Default report language')
  await actor.selectOptions(languageSelect,'pa')
  expect(await screen.findByText('Default report language saved.')).toBeInTheDocument()
  expect(localStorage.getItem('report-language')).toBe('pa')
 })
})

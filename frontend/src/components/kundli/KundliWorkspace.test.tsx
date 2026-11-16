import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as api from '../../services/api'
import type { BirthProfile } from '../../types/api'
import { KundliWorkspace } from './KundliWorkspace'
import { makeKundliCalculation } from './kundliTestFixture'

const location={id:1,city:'Chandigarh',state:'Chandigarh',country:'India',country_code:'IN',latitude:'30.7333000',longitude:'76.7794000',timezone:'Asia/Kolkata',created_at:'2026-01-01T00:00:00'}
const profile={id:41,user_id:null,full_name:'Synthetic Profile',gender:null,birth_date:'2000-01-15',birth_time:'10:30:00',birth_time_unknown:false,location_id:1,location,birth_time_utc:'2000-01-15T05:00:00',utc_offset_minutes:330,timezone_resolution_status:'resolved',timezone_fold:null,notes:null,created_at:'2026-01-01T00:00:00',updated_at:'2026-01-01T00:00:00'} satisfies BirthProfile

describe('KundliWorkspace', () => {
  afterEach(() => vi.restoreAllMocks())

  it('blocks a full chart when birth time is unknown', () => {
    const calculate=vi.spyOn(api,'calculateBirthProfile')
    render(<KundliWorkspace profile={{...profile,birth_time:null,birth_time_unknown:true}} />)
    expect(screen.getByText(/Exact birth time required/)).toBeInTheDocument()
    expect(calculate).not.toHaveBeenCalled()
  })

  it('displays an API calculation failure', async () => {
    vi.spyOn(api,'calculateBirthProfile').mockRejectedValue(new Error('offline'))
    render(<KundliWorkspace profile={profile} />)
    expect(await screen.findByRole('alert')).toHaveTextContent('Kundli could not be calculated')
  })

  it('keeps chart, house details, and table selection synchronized', async () => {
    vi.spyOn(api,'calculateBirthProfile').mockResolvedValue(makeKundliCalculation())
    const user=userEvent.setup(); render(<KundliWorkspace profile={profile} />)
    expect(await screen.findByRole('img',{name:/^North Indian Janam Kundli/})).toBeInTheDocument()
    await user.click(screen.getByRole('button',{name:/House 4/}))
    expect(screen.getByRole('heading',{name:/House 4/})).toBeInTheDocument()
    await user.click(screen.getByRole('row',{name:/Moon/}))
    expect(screen.getByRole('heading',{name:/Moon · Chandra/})).toBeInTheDocument()
    expect(screen.getByRole('row',{name:/Moon/})).toHaveAttribute('aria-selected','true')
  })

  it('exports the actual rendered SVG as a standalone blob', async () => {
    vi.spyOn(api,'calculateBirthProfile').mockResolvedValue(makeKundliCalculation())
    const createObjectURL=vi.fn(()=> 'blob:kundli'), revokeObjectURL=vi.fn()
    Object.defineProperty(URL,'createObjectURL',{value:createObjectURL,configurable:true})
    Object.defineProperty(URL,'revokeObjectURL',{value:revokeObjectURL,configurable:true})
    const click=vi.spyOn(HTMLAnchorElement.prototype,'click').mockImplementation(()=>undefined)
    const user=userEvent.setup(); render(<KundliWorkspace profile={profile} />)
    await user.click(await screen.findByRole('button',{name:/Export SVG/}))
    expect(createObjectURL).toHaveBeenCalledWith(expect.any(Blob))
    expect(click).toHaveBeenCalled()
    expect(revokeObjectURL).toHaveBeenCalledWith('blob:kundli')
  })
})

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { makeKundliCalculation } from '../components/kundli/kundliTestFixture'
import * as api from '../services/api'
import type { BirthProfile, DivisionalChart, DivisionalChartType } from '../types/api'
import { DivisionalChartsPage } from './DivisionalChartsPage'

const profile: BirthProfile = {id:1,full_name:'Test Person',gender:null,birth_date:'2000-01-15',birth_time:'10:30:00',birth_time_unknown:false,location_id:1,location:{id:1,city:'Chandigarh',state:'Chandigarh',country:'India',country_code:'IN',latitude:'30.7333',longitude:'76.7794',timezone:'Asia/Kolkata',created_at:'2026-01-01'},birth_time_utc:'2000-01-15T05:00:00',utc_offset_minutes:330,timezone_resolution_status:'resolved',timezone_fold:null,notes:null,created_at:'2026-01-01',updated_at:'2026-01-01',user_id:null}

function divisional(chartType: DivisionalChartType): DivisionalChart {
  const d1 = makeKundliCalculation()
  return {...d1,chart_type:chartType,chart_name:chartType==='D9'?'Navamsha':'Dashamsha',primary_use:'Calculated positions',lagna:{...d1.lagna,original_longitude:d1.lagna.longitude,original_rashi_number:1,division_number:1,boundary_near:false},planets:d1.planets.map(item=>({...item,original_longitude:item.longitude,original_longitude_formatted:item.longitude_formatted,original_rashi:item.rashi,division_number:1,vargottama:chartType==='D9',boundary_near:false})),calculation:{system:'Parashari',division:chartType==='D9'?9:10,segment_degrees:chartType==='D9'?10/3:3,interval_semantics:'half-open',boundary_warning_degrees:1/60}}
}

describe('DivisionalChartsPage', () => {
  it('loads D1, D9, and D10 and switches accessible chart tabs', async () => {
    vi.spyOn(api,'getBirthProfiles').mockResolvedValue([profile])
    vi.spyOn(api,'calculateBirthProfile').mockResolvedValue(makeKundliCalculation())
    vi.spyOn(api,'getDivisionalProfile').mockImplementation(async (_id, type) => divisional(type))
    const user = userEvent.setup()
    render(<MemoryRouter><DivisionalChartsPage/></MemoryRouter>)
    expect(await screen.findByRole('heading',{name:'D9 · Navamsha'})).toBeInTheDocument()
    expect(screen.getByRole('heading',{name:'D1 · Rashi'})).toBeInTheDocument()
    await user.click(screen.getByRole('tab',{name:'D10 Dashamsha'}))
    expect(screen.getByRole('heading',{name:'D10 · Dashamsha'})).toBeInTheDocument()
    expect(api.getDivisionalProfile).toHaveBeenCalledWith(1,'D9',expect.any(AbortSignal))
    expect(api.getDivisionalProfile).toHaveBeenCalledWith(1,'D10',expect.any(AbortSignal))
  })
})

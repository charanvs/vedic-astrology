import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, expect, it, vi } from 'vitest'
import * as api from '../services/api'
import type { BirthProfile } from '../types/api'
import { SavedProfilesPage } from './SavedProfilesPage'

const profile={id:1,user_id:null,full_name:'Test Person',gender:null,birth_date:'2000-01-15',birth_time:'10:30:00',birth_time_unknown:false,location_id:1,location:{id:1,city:'Chandigarh',state:'Chandigarh',country:'India',country_code:'IN',latitude:'30.7333000',longitude:'76.7794000',timezone:'Asia/Kolkata',created_at:'2026-01-01T00:00:00'},birth_time_utc:'2000-01-15T05:00:00',utc_offset_minutes:330,timezone_resolution_status:'resolved',timezone_fold:null,notes:null,created_at:'2026-01-01T00:00:00',updated_at:'2026-01-01T00:00:00'} satisfies BirthProfile
afterEach(()=>vi.restoreAllMocks())
it('shows loading, saved profiles, view/edit actions and pagination',async()=>{const user=userEvent.setup();const mock=vi.spyOn(api,'listBirthProfiles').mockResolvedValue({items:[profile],total:11,offset:0,limit:10});render(<MemoryRouter><SavedProfilesPage/></MemoryRouter>);expect(screen.getByText('Loading saved profiles…')).toBeInTheDocument();expect(await screen.findByText('Test Person')).toBeInTheDocument();expect(screen.getByRole('link',{name:/View/})).toHaveAttribute('href','/birth-profiles/1');await user.click(screen.getByRole('button',{name:'Next page'}));await waitFor(()=>expect(mock).toHaveBeenLastCalledWith(expect.objectContaining({offset:10,limit:10})))})
it('supports name search and API failure states',async()=>{const user=userEvent.setup();const mock=vi.spyOn(api,'listBirthProfiles').mockResolvedValueOnce({items:[],total:0,offset:0,limit:10}).mockRejectedValueOnce(new Error('offline'));render(<MemoryRouter><SavedProfilesPage/></MemoryRouter>);await screen.findByText('No matching birth profiles');await user.type(screen.getByPlaceholderText('Search profiles by name'),'Anita');await user.click(screen.getByRole('button',{name:'Search'}));expect(await screen.findByRole('alert')).toHaveTextContent('Saved profiles could not be loaded');expect(mock).toHaveBeenLastCalledWith(expect.objectContaining({search:'Anita'}))})

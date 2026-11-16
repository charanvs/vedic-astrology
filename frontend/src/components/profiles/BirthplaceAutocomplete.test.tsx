import {render,screen,waitFor} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import {afterEach,describe,expect,it,vi} from 'vitest'
import * as api from '../../services/api'
import type {Location} from '../../types/api'
import {BirthplaceAutocomplete} from './BirthplaceAutocomplete'

const jaipur:Location={id:3,city:'Jaipur',state:'Rajasthan',country:'India',country_code:'IN',latitude:'26.9124338',longitude:'75.7872709',timezone:'Asia/Kolkata',created_at:'2026-01-01T00:00:00'}

describe('BirthplaceAutocomplete',()=>{
 afterEach(()=>vi.restoreAllMocks())

 it('pre-fills the location form with a chosen offline geocoding suggestion instead of selecting it immediately',async()=>{
  const user=userEvent.setup()
  vi.spyOn(api,'searchLocations').mockResolvedValue({items:[],total:0,offset:0,limit:10})
  vi.spyOn(api,'searchGeocoding').mockResolvedValue([{name:'Jaipur',state:'Rajasthan',country:'India',country_code:'IN',latitude:'26.9124338',longitude:'75.7872709',timezone:'Asia/Kolkata'}])
  const onSelect=vi.fn()
  render(<BirthplaceAutocomplete value={null} onSelect={onSelect}/>)
  await user.type(screen.getByRole('combobox',{name:'Place of birth'}),'Jaipur')
  await user.click(await screen.findByText('Jaipur, Rajasthan, India'))
  expect(onSelect).not.toHaveBeenCalled()
  expect(await screen.findByText(/Coordinates and timezone were filled in from an offline city database/)).toBeInTheDocument()
  expect(screen.getByLabelText('City')).toHaveValue('Jaipur')
  expect(screen.getByLabelText('Latitude')).toHaveValue(26.9124338)
  expect(screen.getByLabelText('IANA timezone')).toHaveValue('Asia/Kolkata')
 })

 it('still selects an already-verified stored location immediately, without the suggestion workflow',async()=>{
  const user=userEvent.setup()
  vi.spyOn(api,'searchLocations').mockResolvedValue({items:[jaipur],total:1,offset:0,limit:10})
  vi.spyOn(api,'searchGeocoding').mockResolvedValue([])
  const onSelect=vi.fn()
  render(<BirthplaceAutocomplete value={null} onSelect={onSelect}/>)
  await user.type(screen.getByRole('combobox',{name:'Place of birth'}),'Jaipur')
  await user.click(await screen.findByText('Jaipur, Rajasthan, India'))
  expect(onSelect).toHaveBeenCalledWith(jaipur)
 })

 it('does not let a geocoding failure block verified-location results', async () => {
  const user=userEvent.setup()
  vi.spyOn(api,'searchLocations').mockResolvedValue({items:[jaipur],total:1,offset:0,limit:10})
  vi.spyOn(api,'searchGeocoding').mockRejectedValue(new Error('offline dataset unavailable'))
  render(<BirthplaceAutocomplete value={null} onSelect={vi.fn()}/>)
  await user.type(screen.getByRole('combobox',{name:'Place of birth'}),'Jaipur')
  await waitFor(()=>expect(screen.getByText('Jaipur, Rajasthan, India')).toBeInTheDocument())
 })
})

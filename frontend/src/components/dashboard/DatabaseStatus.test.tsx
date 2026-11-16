import {render,screen} from '@testing-library/react'
import {afterEach,expect,it,vi} from 'vitest'
import * as api from '../../services/api'
import {DatabaseStatus} from './DatabaseStatus'
afterEach(()=>vi.restoreAllMocks())
it('shows actual database success',async()=>{vi.spyOn(api,'getDatabaseHealth').mockResolvedValue({status:'ok',database:'connected'});render(<DatabaseStatus/>);expect(await screen.findByText('Database Connected')).toBeInTheDocument()})
it('shows database failure',async()=>{vi.spyOn(api,'getDatabaseHealth').mockRejectedValue(new Error('offline'));render(<DatabaseStatus/>);expect(await screen.findByText('Database Unavailable')).toBeInTheDocument()})

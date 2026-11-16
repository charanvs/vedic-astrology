import { AxiosError, AxiosHeaders, type AxiosResponse } from 'axios'
import { describe, expect, it } from 'vitest'
import { apiErrorMessage, decodeBlobError } from './api'

function blobError(body: string, type: string, status = 503) {
  const config = { headers: new AxiosHeaders() }
  const response = { data: new Blob([body], { type }), status, statusText: '', headers: {}, config } as AxiosResponse
  return new AxiosError('Request failed', 'ERR_BAD_RESPONSE', config, {}, response)
}

describe('PDF error decoding', () => {
  it('shows the server explanation instead of a bare status code', async () => {
    const error = blobError(JSON.stringify({ detail: 'PDF reports are not available on this server yet' }), 'application/json')
    await expect(decodeBlobError(error)).rejects.toBe(error)
    expect(apiErrorMessage(error, 'PDF report could not be generated.')).toBe('PDF reports are not available on this server yet')
  })

  it('falls back to the generic message when the body is not JSON', async () => {
    const error = blobError('<html>Bad gateway</html>', 'text/html', 502)
    await expect(decodeBlobError(error)).rejects.toBe(error)
    expect(apiErrorMessage(error, 'PDF report could not be generated.')).toBe('PDF report could not be generated. (HTTP 502)')
  })
})

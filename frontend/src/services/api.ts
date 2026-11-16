import axios from 'axios'
import type { AstrologyCalculation, AstrologyConfig, BirthProfile, BirthProfileInput, BirthTimeValidation, DatabaseHealth, DashaConfig, DashaResult, DashaYearConvention, DivisionalChart, DivisionalChartType, DivisionalConfig, GeocodingSuggestion, HealthResponse, KundliReportRequest, Location, LocationInput, MatchingConfig, MatchingReportRequest, MatchingResult, MatchingRole, PagedResult, PanchangConfig, PanchangResult, ReportConfig, ReportLanguage } from '../types/api'
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.BASE_URL
export const apiClient = axios.create({ baseURL: apiBaseUrl, timeout: 5000, withCredentials:true, headers: { Accept: 'application/json' } })
let csrfToken:string|null=null
export function setCsrfToken(value:string|null){csrfToken=value}
apiClient.interceptors.request.use((config)=>{if(csrfToken&&config.method&&!['get','head','options'].includes(config.method.toLowerCase()))config.headers.set('X-CSRF-Token',csrfToken);return config})
apiClient.interceptors.response.use(response=>response,error=>{if(axios.isAxiosError(error)&&error.response?.status===401){setCsrfToken(null);window.dispatchEvent(new Event('vedic-auth-expired'))}return Promise.reject(error)})
export type AuthUser={id:number;full_name:string;email:string;email_verified:boolean;approved:boolean;is_active:boolean;role:'user'|'admin';created_at:string;last_login_at:string|null;deletion_requested_at:string|null}
export async function getCurrentUser(){return (await apiClient.get<AuthUser>('api/auth/me')).data}
export async function refreshCsrf(){const value=(await apiClient.get<{csrf_token:string}>('api/auth/csrf')).data.csrf_token;setCsrfToken(value);return value}
export async function loginAccount(data:{email:string;password:string}){const response=await apiClient.post<{user:AuthUser;csrf_token:string}>('api/auth/login',data);setCsrfToken(response.data.csrf_token);return response.data.user}
export async function registerAccount(data:{full_name:string;email:string;password:string;accept_terms:boolean}){return (await apiClient.post<{message:string;development_token?:string}>('api/auth/register',data)).data}
export async function verifyEmail(token:string){return (await apiClient.post<{message:string}>('api/auth/verify-email',{token})).data}
export async function forgotPassword(email:string){return (await apiClient.post<{message:string;development_token?:string}>('api/auth/forgot-password',{email})).data}
export async function resetPassword(token:string,password:string){return (await apiClient.post<{message:string}>('api/auth/reset-password',{token,password})).data}
export async function logoutAccount(){const result=(await apiClient.post<{message:string}>('api/auth/logout')).data;setCsrfToken(null);return result}
export async function changePassword(current_password:string,new_password:string){const result=(await apiClient.post<{message:string}>('api/auth/change-password',{current_password,new_password})).data;await refreshCsrf();return result}
export async function getSessions(){return (await apiClient.get<Array<{id:string;created_at:string;last_activity_at:string;expires_at:string;current:boolean;user_agent:string|null}>>('api/auth/sessions')).data}
export async function revokeSession(id:string){return (await apiClient.delete<{message:string}>('api/auth/sessions/'+id)).data}
export async function requestAccountDeletion(current_password:string){return (await apiClient.post<{message:string}>('api/account/deletion-request',{current_password,confirmation:'DELETE MY ACCOUNT'})).data}
export type Preferences={theme:'light'|'dark'|'system'|null;report_language:ReportLanguage|null;dasha_year_convention:DashaYearConvention|null;matching_ruleset:string|null}
export type AccountStatus='pending'|'approved'|'inactive'
export type AdminUser={id:number;full_name:string;email:string;role:'user'|'admin';status:AccountStatus;email_verified:boolean;approved_at:string|null;created_at:string;last_login_at:string|null;deletion_requested_at:string|null;profile_count:number}
export type AdminSummary=Record<AccountStatus|'all',number>
export async function getAdminSummary(){return (await apiClient.get<AdminSummary>('api/admin/summary')).data}
export async function listAdminUsers(status:AccountStatus|'all'){return (await apiClient.get<AdminUser[]>('api/admin/users',{params:{status}})).data}
export async function changeUserStatus(id:number,action:'approve'|'deactivate'|'reactivate'){return (await apiClient.post<AdminUser>(`api/admin/users/${id}/${action}`)).data}
export async function getPreferences(){return (await apiClient.get<Preferences>('api/account/preferences')).data}
export async function updatePreferences(data:Partial<Preferences>){return (await apiClient.patch<Preferences>('api/account/preferences',data)).data}
export async function exportAccount(){return (await apiClient.get('api/account/export')).data}
export async function getHealth(): Promise<HealthResponse> { const response = await apiClient.get<HealthResponse>('api/health'); return response.data }
export async function getDatabaseHealth(){return (await apiClient.get<DatabaseHealth>('api/db-health')).data}
export async function searchLocations(params:{search?:string;country?:string;state?:string;offset?:number;limit?:number}={},signal?:AbortSignal):Promise<PagedResult<Location>>{const response=await apiClient.get<Location[]>('api/locations',{params,signal});return {items:response.data,total:Number(response.headers['x-total-count']??response.data.length),offset:params.offset??0,limit:params.limit??20}}
export async function getLocations(){return (await searchLocations({limit:100})).items}
export async function getLocation(id:number){return (await apiClient.get<Location>(`api/locations/${id}`)).data}
export async function createLocation(data:LocationInput){return (await apiClient.post<Location>('api/locations',data)).data}
export async function searchGeocoding(query:string,signal?:AbortSignal){if(query.trim().length<2)return [];return (await apiClient.get<GeocodingSuggestion[]>('api/geocoding/search',{params:{q:query.trim(),limit:8},signal})).data}
export async function updateLocation(id:number,data:Partial<LocationInput>){return (await apiClient.patch<Location>(`api/locations/${id}`,data)).data}
export async function createBirthProfile(data:BirthProfileInput){return (await apiClient.post<BirthProfile>('api/birth-profiles',data)).data}
export async function getBirthProfiles(limit=5){return (await apiClient.get<BirthProfile[]>('api/birth-profiles',{params:{limit}})).data}
export async function listBirthProfiles(params:{search?:string;offset?:number;limit?:number}={}):Promise<PagedResult<BirthProfile>>{const response=await apiClient.get<BirthProfile[]>('api/birth-profiles',{params});return {items:response.data,total:Number(response.headers['x-total-count']??response.data.length),offset:params.offset??0,limit:params.limit??20}}
export async function getBirthProfile(id:number){return (await apiClient.get<BirthProfile>(`api/birth-profiles/${id}`)).data}
export async function updateBirthProfile(id:number,data:Partial<BirthProfileInput>){return (await apiClient.patch<BirthProfile>(`api/birth-profiles/${id}`,data)).data}
export async function validateBirthTime(data:{birth_date:string;birth_time:string;timezone:string;fold?:number|null}){return (await apiClient.post<BirthTimeValidation>('api/birth-time/validate',data)).data}
export async function calculateBirthProfile(id:number){return (await apiClient.get<AstrologyCalculation>(`api/astrology/birth-profiles/${id}/calculate`)).data}
export async function getAstrologyConfig(){return (await apiClient.get<AstrologyConfig>('api/astrology/config')).data}
export async function getDailyPanchang(date:string,locationId:number,signal?:AbortSignal){return (await apiClient.get<PanchangResult>('api/panchang/daily',{params:{date,location_id:locationId},signal,timeout:15000})).data}
export async function calculatePanchang(data:{date:string;latitude:number;longitude:number;timezone:string;elevation?:number;city?:string;state?:string|null;country?:string}){return (await apiClient.post<PanchangResult>('api/panchang/calculate',data,{timeout:15000})).data}
export async function getPanchangConfig(){return (await apiClient.get<PanchangConfig>('api/panchang/config')).data}
export async function getDashaProfile(profileId:number,yearConvention:DashaYearConvention,referenceDatetime?:string,signal?:AbortSignal){return (await apiClient.get<DashaResult>(`api/dasha/birth-profiles/${profileId}`,{params:{year_convention:yearConvention,reference_datetime:referenceDatetime||undefined,detail_level:'pratyantardasha'},signal,timeout:15000})).data}
export async function getDashaConfig(){return (await apiClient.get<DashaConfig>('api/dasha/config')).data}
export async function calculateProfileMatching(data:{partner_one_profile_id:number;partner_two_profile_id:number;partner_one_role:MatchingRole;partner_two_role:MatchingRole;ruleset?:string}){return (await apiClient.post<MatchingResult>('api/matching/birth-profiles',data,{timeout:15000})).data}
export async function getMatchingConfig(){return (await apiClient.get<MatchingConfig>('api/matching/config')).data}
export async function getDivisionalProfile(profileId:number,chartType:DivisionalChartType,signal?:AbortSignal){return (await apiClient.get<DivisionalChart>(`api/divisional/birth-profiles/${profileId}/${chartType.toLowerCase()}`,{signal,timeout:15000})).data}
export async function getDivisionalConfig(){return (await apiClient.get<DivisionalConfig>('api/divisional/config')).data}
export async function getReportConfig(){return (await apiClient.get<ReportConfig>('api/reports/config')).data}
// PDF requests use responseType 'blob', so error bodies arrive as a Blob; decode them so the real reason is shown.
export async function decodeBlobError(error:unknown):Promise<never>{if(axios.isAxiosError(error)&&error.response?.data instanceof Blob){try{error.response.data=JSON.parse(await error.response.data.text())}catch{/* not JSON: keep the generic message */}}throw error}
export async function generateKundliReport(data:KundliReportRequest,preview=false){try{return (await apiClient.post<Blob>(preview?'api/reports/preview':'api/reports/kundli',data,{responseType:'blob',timeout:60000})).data}catch(error){return decodeBlobError(error)}}
export async function generateMatchingReport(data:MatchingReportRequest){try{return (await apiClient.post<Blob>('api/reports/matching',data,{responseType:'blob',timeout:60000})).data}catch(error){return decodeBlobError(error)}}
/** The same report as a print-ready HTML page, for servers that cannot render PDFs. */
export async function generatePrintableReport(kind:'kundli'|'matching',data:KundliReportRequest|MatchingReportRequest){return (await apiClient.post<string>(`api/reports/${kind}/printable`,data,{responseType:'text',timeout:60000})).data}
export function apiErrorMessage(error:unknown,fallback='The request could not be completed.'){if(axios.isAxiosError(error)){const detail=error.response?.data?.detail;if(typeof detail==='string')return detail;if(Array.isArray(detail))return detail.map((item:{msg?:string})=>item.msg).filter(Boolean).join(' · ')||fallback;if(error.code==='ERR_CANCELED')return '';if(!error.response)return 'The server could not be reached. Check your internet connection and try again.';return `${fallback} (HTTP ${error.response.status})`}return fallback}

import {createContext,useCallback,useContext,useEffect,useMemo,useState,type ReactNode} from 'react'
import {getCurrentUser,getPreferences,loginAccount,logoutAccount,refreshCsrf,setCsrfToken,updatePreferences as patchPreferences,type AuthUser,type Preferences} from '../services/api'
import {useTheme} from './useTheme'
type AuthValue={user:AuthUser|null;loading:boolean;preferences:Preferences|null;login:(email:string,password:string)=>Promise<void>;logout:()=>Promise<void>;refresh:()=>Promise<void>;updatePreferences:(patch:Partial<Preferences>)=>Promise<void>}
const AuthContext=createContext<AuthValue|undefined>(undefined)
function hydratePreferences(prefs:Preferences,setTheme:(value:'light'|'dark'|'system')=>void){
 if(prefs.theme)setTheme(prefs.theme)
 if(prefs.report_language)localStorage.setItem('report-language',prefs.report_language)
 if(prefs.dasha_year_convention)localStorage.setItem('dasha-year-convention',prefs.dasha_year_convention)
}
export function AuthProvider({children}:{children:ReactNode}){
 const [user,setUser]=useState<AuthUser|null>(null);const [loading,setLoading]=useState(true)
 const [preferences,setPreferences]=useState<Preferences|null>(null)
 const {setTheme}=useTheme()
 const refresh=useCallback(async()=>{
  try{
   const next=await getCurrentUser();setUser(next);await refreshCsrf()
   const prefs=await getPreferences().catch(()=>null);setPreferences(prefs)
   if(prefs)hydratePreferences(prefs,setTheme)
  }catch{setUser(null);setCsrfToken(null);setPreferences(null)}
  finally{setLoading(false)}
 },[setTheme])
 useEffect(()=>{void refresh();const expired=()=>{setUser(null);setCsrfToken(null);setPreferences(null)};window.addEventListener('vedic-auth-expired',expired);return()=>window.removeEventListener('vedic-auth-expired',expired)},[refresh])
 const login=useCallback(async(email:string,password:string)=>{
  setUser(await loginAccount({email,password}))
  const prefs=await getPreferences().catch(()=>null);setPreferences(prefs)
  if(prefs)hydratePreferences(prefs,setTheme)
 },[setTheme])
 const logout=useCallback(async()=>{await logoutAccount();setUser(null);setPreferences(null)},[])
 const updatePreferences=useCallback(async(patch:Partial<Preferences>)=>{setPreferences(await patchPreferences(patch))},[])
 const value=useMemo(()=>({user,loading,preferences,login,logout,refresh,updatePreferences}),[user,loading,preferences,login,logout,refresh,updatePreferences])
 return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
export function useAuth(){const value=useContext(AuthContext);if(!value)throw new Error('useAuth must be used within AuthProvider');return value}

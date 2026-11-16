import type { AstrologyCalculation } from '../../types/api'

const names = ['Mesha','Vrishabha','Mithuna','Karka','Simha','Kanya','Tula','Vrishchika','Dhanu','Makara','Kumbha','Meena']
const english = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']

export function makeKundliCalculation(lagnaRashi = 1): AstrologyCalculation {
  const moonRashi = { number: lagnaRashi, name: names[lagnaRashi - 1], english_name: english[lagnaRashi - 1], hindi_name: '', longitude_within: 4.5 }
  return {
    birth_datetime:{local_datetime:'2000-01-15T10:30:00',utc_datetime:'2000-01-15T05:00:00Z',timezone:'Asia/Kolkata',resolution_status:'resolved'},
    location:{city:'Chandigarh',state:'Chandigarh',country:'India',latitude:30.7333,longitude:76.7794},
    settings:{zodiac:'sidereal',ayanamsa:'Lahiri (Chitrapaksha)',ayanamsa_mode:'SIDM_LAHIRI',planetary_reference:'geocentric',node_convention:'mean lunar node',house_system:'whole-sign from ascendant Rashi',calendar:'proleptic Gregorian',ephemeris_source:'moshier',stationary_threshold:0.0001},
    julian_day_ut:2451558.7,julian_day_calendar:'proleptic Gregorian',ayanamsa:{degrees:23.85,formatted:'23° 51′ 00.000″',mode:'SIDM_LAHIRI',name:'Lahiri (Chitrapaksha)'},
    lagna:{longitude:(lagnaRashi-1)*30+4.5,longitude_formatted:'4° 30′ 00.000″',rashi:moonRashi,method:'houses_ex',whole_sign_houses:[]},
    planets:[{identifier:'moon',english_name:'Moon',sanskrit_name:'Chandra',hindi_name:'चन्द्र',longitude:(lagnaRashi-1)*30+4.5,longitude_formatted:'4° 30′ 00.000″',latitude:0,longitude_speed:-13,motion:'retrograde',retrograde:true,rashi:moonRashi,nakshatra:{number:1,name:'Ashwini',pada:2,longitude_within:4.5,lord:'Ketu'},house:1,calculation_flags:65860,ephemeris_source:'Moshier analytical ephemeris',convention:'test'}],
    houses:Array.from({length:12},(_,index)=>{const number=((lagnaRashi-1+index)%12)+1;return {house_number:index+1,rashi_number:number,rashi_name:names[number-1],rashi_english_name:english[number-1],rashi_hindi_name:'',planet_identifiers:index===0?['moon']:[],is_lagna:index===0}}),
    whole_sign_houses:[],engine:{engine:'Swiss Ephemeris',engine_version:'2.10.03',binding:'pyswisseph',binding_version:'2.10.3.2',ephemeris_source:'Moshier analytical ephemeris',calculation_duration_ms:1},warnings:[]
  }
}

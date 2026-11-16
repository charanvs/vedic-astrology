import type { BirthProfile, KootaScore, MatchingResult } from '../../types/api'

const location={id:2,city:'Sangrur',state:'Punjab',country:'India',country_code:'IN',latitude:'30.25',longitude:'75.84',timezone:'Asia/Kolkata',created_at:'2026-11-13T00:00:00'}
export const matchingProfiles:BirthProfile[]=[
 {id:1,user_id:null,full_name:'Rohini Partner',gender:null,birth_date:'1990-01-01',birth_time:'10:00:00',birth_time_unknown:false,location_id:2,birth_time_utc:'1990-01-01T04:30:00',utc_offset_minutes:330,timezone_resolution_status:'resolved',timezone_fold:null,notes:null,created_at:'2026-11-13T00:00:00',updated_at:'2026-11-13T00:00:00',location},
 {id:2,user_id:null,full_name:'Hasta Partner',gender:null,birth_date:'1992-02-02',birth_time:null,birth_time_unknown:true,location_id:2,birth_time_utc:null,utc_offset_minutes:null,timezone_resolution_status:'unknown_time',timezone_fold:null,notes:null,created_at:'2026-11-13T00:00:00',updated_at:'2026-11-13T00:00:00',location:{...location,id:3,city:'Chandigarh',state:'Chandigarh'}},
]
const rows:[string,string,number,number,string,string][]=[
 ['varna','Varna',1,1,'Vaishya','Vaishya'],['vashya','Vashya',.5,2,'Chatushpada','Dvipada'],['tara','Tara (Dina)',3,3,'Janma','Janma'],['yoni','Yoni',2,4,'Serpent','Buffalo'],['graha_maitri','Graha Maitri',5,5,'Venus','Mercury'],['gana','Gana',6,6,'Manushya','Deva'],['bhakoot','Bhakoot',0,7,'Vrishabha','Kanya'],['nadi','Nadi',8,8,'Antya','Adi'],
]
const kootas:KootaScore[]=rows.map(([id,name,score,maximum,first,second])=>({id,name,score:String(score),maximum:String(maximum),partner_one_classification:first,partner_two_classification:second,explanation:`${name} explanation from the selected ruleset.`,rule_id:`TEST-${id}`,details:{},directional:['varna','vashya','tara','yoni','graha_maitri','gana'].includes(id)}))
export const matchingResult:MatchingResult={status:'definitive',ruleset:{id:'muhurta_chintamani_joshi_v1',name:'Muhurta Chintamani — Kedar Datt Joshi charts',version:'1.0.0',tradition:'North Indian Ashtakoota Guna Milan',source:'Test source',role_order:'bride row, groom column'},partners:[
 {profile_id:1,name:'Rohini Partner',role:'bride',moon:{sidereal_longitude:'45',degree_in_rashi:'15',rashi_number:2,rashi:'Vrishabha',rashi_lord:'Venus',nakshatra_number:4,nakshatra:'Rohini',pada:2,yoni:'Serpent',gana:'Manushya',nadi:'Antya',precision:'exact',uncertainty_start_utc:null,uncertainty_end_utc:null}},
 {profile_id:2,name:'Hasta Partner',role:'groom',moon:{sidereal_longitude:'168',degree_in_rashi:'18',rashi_number:6,rashi:'Kanya',rashi_lord:'Mercury',nakshatra_number:13,nakshatra:'Hasta',pada:3,yoni:'Buffalo',gana:'Deva',nadi:'Adi',precision:'date_unambiguous',uncertainty_start_utc:'1992-02-01T18:30:00Z',uncertainty_end_utc:'1992-02-02T18:30:00Z'}},
],kootas,total_score:'25.5',maximum_score:'36',percentage:'70.833333',threshold:{value:'18',met:true,label:'At or above a commonly used traditional threshold'},observations:[
 {id:'nadi_dosha',name:'Nadi observation',triggered:false,triggering_rule:'TEST-nadi',inputs:{},exception_evaluated:false,explanation:'Different Nadi groups.'},
 {id:'bhakoot_dosha',name:'Bhakoot observation',triggered:true,triggering_rule:'TEST-bhakoot',inputs:{},exception_evaluated:false,explanation:'A 5/9 relationship is flagged.'},
 {id:'gana_observation',name:'Gana observation',triggered:false,triggering_rule:'TEST-gana',inputs:{},exception_evaluated:false,explanation:'No low Gana value.'},
],metadata:{},warnings:[]}

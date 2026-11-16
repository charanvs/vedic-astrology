export const dashaColors:Record<string,string>={Ketu:'#8b5cf6',Venus:'#ec4899',Sun:'#f97316',Moon:'#64748b',Mars:'#dc2626',Rahu:'#475569',Jupiter:'#eab308',Saturn:'#2563eb',Mercury:'#16a34a'}

export function formatDashaDate(value:string,timezone:string,withTime=true){
 return new Intl.DateTimeFormat('en-IN',{timeZone:timezone,dateStyle:'medium',...(withTime?{timeStyle:'short'}:{})}).format(new Date(value))
}

export function decimalLabel(value:string|number,digits=2){return Number(value).toFixed(digits)}

export function remainingLabel(seconds:string){const days=Math.max(0,Number(seconds)/86400);if(days>=365.25)return `${(days/365.25).toFixed(2)} years`;if(days>=30)return `${(days/30.4375).toFixed(1)} months`;return `${days.toFixed(1)} days`}

export function utcInputNow(){return new Date().toISOString().slice(0,16)}
export function utcInputToIso(value:string){return value?`${value}:00Z`:undefined}

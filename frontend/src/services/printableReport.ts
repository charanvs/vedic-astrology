export class PopupBlockedError extends Error{constructor(){super('Your browser blocked the new tab. Allow pop-ups for this site, then try again.');this.name='PopupBlockedError'}}

const placeholder='<!doctype html><title>Preparing report…</title><p style="font:16px sans-serif;padding:2rem">Preparing your report…</p>'

/** Writes the report into the tab, then opens the print dialog once the page and its fonts have loaded. */
function showPrintable(win:Window,html:string){
 const print=()=>{try{win.focus();win.print()}catch{/* the reader can still print from the browser menu */}}
 win.addEventListener('load',()=>{const fonts=win.document.fonts;if(fonts)fonts.ready.then(()=>setTimeout(print,250),print);else setTimeout(print,800)},{once:true})
 win.document.open();win.document.write(html);win.document.close()
}

/**
 * Opens a print-ready report in a new tab. Call it directly from a click handler: the tab is opened
 * before anything is awaited, so pop-up blockers allow it. The tab is closed again if loading fails.
 */
export async function openPrintableReport(load:()=>Promise<string>){
 const win=window.open('','_blank')
 if(!win)throw new PopupBlockedError()
 win.document.write(placeholder)
 let html:string
 try{html=await load()}catch(error){win.close();throw error}
 showPrintable(win,html)
}

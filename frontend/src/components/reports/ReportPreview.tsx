import { Download, FileText } from 'lucide-react'

export function ReportPreview({url,onDownload}:{url:string;onDownload:()=>void}){
 return <section className="space-y-3" aria-labelledby="pdf-preview-heading"><div className="flex flex-wrap items-center justify-between gap-3"><h2 id="pdf-preview-heading" className="flex items-center gap-2 text-xl font-bold"><FileText className="size-5"/>PDF preview</h2><button onClick={onDownload} className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-[var(--primary-strong)] px-4 font-bold text-white"><Download className="size-4"/>Download PDF</button></div><object data={url} type="application/pdf" className="h-[75vh] min-h-[520px] w-full rounded-2xl border border-[var(--border)]"><p>Embedded PDF preview is unavailable. Use Download PDF.</p></object></section>
}

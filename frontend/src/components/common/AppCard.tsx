import type {HTMLAttributes,ReactNode} from 'react'
export function AppCard({children,className='',...props}:HTMLAttributes<HTMLDivElement>&{children:ReactNode}){return <div className={`rounded-2xl border border-[var(--border)] bg-[var(--surface)] shadow-sm ${className}`} {...props}>{children}</div>}

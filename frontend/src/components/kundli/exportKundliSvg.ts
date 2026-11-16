export function exportKundliSvg(svg: SVGSVGElement | null, filename: string, metadataText: string) {
  if (!svg) return
  const clone = svg.cloneNode(true) as SVGSVGElement
  const metadata = document.createElementNS('http://www.w3.org/2000/svg', 'metadata')
  metadata.textContent = metadataText
  clone.prepend(metadata)
  clone.setAttribute('style', 'background:#fffdfa;color:#29231f')
  clone.querySelectorAll<SVGElement>('*').forEach((element) => {
    const style = window.getComputedStyle(element)
    if (style.fill && style.fill !== 'none') element.setAttribute('fill', style.fill)
    if (style.stroke && style.stroke !== 'none') element.setAttribute('stroke', style.stroke)
    element.removeAttribute('class'); element.removeAttribute('tabindex'); element.removeAttribute('role'); element.removeAttribute('aria-pressed')
  })
  const source = `<?xml version="1.0" encoding="UTF-8"?>\n${new XMLSerializer().serializeToString(clone)}`
  const url = URL.createObjectURL(new Blob([source], { type: 'image/svg+xml;charset=utf-8' }))
  const anchor = document.createElement('a')
  anchor.href = url; anchor.download = filename; anchor.click()
  URL.revokeObjectURL(url)
}

import { useEffect, useId, useRef, useState } from 'react'
import type { Mermaid } from 'mermaid'

let isInitialized = false

function initializeMermaidOnce(mermaid: Mermaid): void {
  if (isInitialized) return
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  mermaid.initialize({
    startOnLoad: false,
    theme: prefersDark ? 'dark' : 'default',
    // Diagram source ultimately comes from lesson content — currently
    // only our own seed data, but 'strict' sanitizes any HTML/script in
    // labels regardless, which is cheap defense-in-depth to have from
    // the start rather than retrofit later.
    securityLevel: 'strict',
  })
  isInitialized = true
}

interface MermaidDiagramProps {
  chart: string
}

export function MermaidDiagram({ chart }: MermaidDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [error, setError] = useState<string | null>(null)
  // useId() can include colons, which aren't safe inside the id mermaid
  // generates internally for referencing SVG elements — stripped here.
  const diagramId = useId().replace(/:/g, '')

  useEffect(() => {
    let cancelled = false

    // Dynamic import, not a top-level static one: mermaid's core library
    // is large (several hundred KB, even before any diagram-type-specific
    // code it lazy-loads internally). A static `import mermaid from
    // 'mermaid'` at the top of this file would bundle that cost into
    // every page's main chunk — including pages with no diagram at all
    // (login, chat, home) — since this component is imported directly by
    // LessonPage. Importing it here means it's only fetched the moment a
    // lesson containing an actual diagram is viewed.
    import('mermaid')
      .then(({ default: mermaid }) => {
        if (cancelled) return undefined
        initializeMermaidOnce(mermaid)
        return mermaid.render(`mermaid-${diagramId}`, chart)
      })
      .then((result) => {
        if (!cancelled && result && containerRef.current) {
          containerRef.current.innerHTML = result.svg
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : 'Failed to render diagram.',
          )
        }
      })

    return () => {
      cancelled = true
    }
  }, [chart, diagramId])

  if (error) {
    return <p className="form-error">Diagram error: {error}</p>
  }

  return <div className="mermaid-diagram" ref={containerRef} />
}

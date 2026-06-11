// utils/format.js — Formattazione condivisa
// Le date nell'applicativo si mostrano sempre in formato italiano dd/mm/yyyy.

/** '2026-06-15' | '2026-06-15T08:00:00' | Date → '15/06/2026' */
export function formatDataIT(v) {
  if (!v) return '—'
  const s = typeof v === 'string' ? v : String(v)
  const [y, m, d] = s.slice(0, 10).split('-')
  if (!y || !m || !d) return s
  return `${d}/${m}/${y}`
}

/** '2026-06-15T14:30:00' → '15/06/2026 14:30' */
export function formatDataOraIT(v) {
  if (!v) return '—'
  const s = String(v).replace('T', ' ')
  const data = formatDataIT(s)
  const ora  = s.slice(11, 16)
  return ora ? `${data} ${ora}` : data
}

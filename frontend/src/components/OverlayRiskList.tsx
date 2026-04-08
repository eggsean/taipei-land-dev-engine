import { Alert } from 'antd'
import type { OverlayRisk } from '../types'

const typeMap: Record<string, 'warning' | 'error' | 'info'> = {
  urban_design_review: 'warning',
  hillside: 'error',
  cultural_heritage: 'error',
  eia: 'warning',
}

export default function OverlayRiskList({ risks }: { risks: OverlayRisk[] }) {
  if (risks.length === 0) return null
  return (
    <div style={{ marginBottom: 16 }}>
      {risks.map((r, i) => (
        <Alert
          key={i}
          message={r.description}
          type={typeMap[r.risk_type] || 'info'}
          showIcon
          style={{ marginBottom: 8 }}
        />
      ))}
    </div>
  )
}

import { Card } from 'antd'
import type { ChecklistItem } from '../types'
import StatusBadge from './StatusBadge'

export default function ChecklistDetailCards({ items }: { items: ChecklistItem[] }) {
  return (
    <>
      {items
        .filter((c) => c.status !== null)
        .map((c) => (
          <Card
            key={c.point_number}
            title={`${c.point_number}. ${c.title}`}
            extra={c.status && <StatusBadge status={c.status} />}
            style={{ marginBottom: 16 }}
            size="small"
          >
            {c.notes.length > 0 && (
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                {c.notes.map((n, i) => (
                  <li key={i}>{n}</li>
                ))}
              </ul>
            )}
          </Card>
        ))}
    </>
  )
}

import { Card, Descriptions } from 'antd'
import type { ModuleResult } from '../types'
import StatusBadge from './StatusBadge'

const MODULE_LABELS: Record<string, string> = {
  zoning: '1-2. 分區 / 用途判定',
  building_line: '4. 建築線前置判定',
  road_frontage: '4. 臨路判定',
  odd_lot: '3. 畸零地初判',
  far_bcr: '6-7. 容積率 / 建蔽率',
  coverage: '7. 建蔽率',
  parking: '12. 停車數量初算',
  overlays: '14-17. 特殊疊圖風險',
  far_bonus: '8. 容積獎勵',
  far_transfer: '9. 容積移轉',
  building_mass: '10. 建築量體',
  fire_safety: '11. 防火間距 / 開口限制',
  traffic: '13. 車道 / 交通動線',
  urban_renewal: '18. 都市更新 / 危老審議',
  building_permit: '5,19. 建造執照核發',
}

export default function ResultCard({ result }: { result: ModuleResult }) {
  const label = MODULE_LABELS[result.module] || result.module

  return (
    <Card
      title={label}
      extra={<StatusBadge status={result.status} />}
      style={{ marginBottom: 16 }}
      size="small"
    >
      {result.notes.length > 0 && (
        <ul style={{ margin: 0, paddingLeft: 20 }}>
          {result.notes.map((n, i) => (
            <li key={i}>{n}</li>
          ))}
        </ul>
      )}
      {Object.keys(result.result).length > 0 && (
        <Descriptions size="small" column={2} style={{ marginTop: 12 }}>
          {Object.entries(result.result)
            .filter(([, v]) => typeof v !== 'object')
            .map(([k, v]) => (
              <Descriptions.Item key={k} label={k}>
                {String(v)}
              </Descriptions.Item>
            ))}
        </Descriptions>
      )}
    </Card>
  )
}

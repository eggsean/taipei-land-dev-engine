import { Alert, Card, Typography } from 'antd'
import type { EvaluationReport } from '../types'
import StatusBadge from './StatusBadge'

const { Title, Text } = Typography

export default function ReportSummary({ report }: { report: EvaluationReport }) {
  return (
    <Card style={{ marginBottom: 24, textAlign: 'center' }}>
      {report.data_mode === 'mock' && (
        <Alert
          message="Demo 模式"
          description="目前使用模擬資料，結論僅供參考，不代表正式法規判定。"
          type="warning"
          showIcon
          style={{ marginBottom: 16, textAlign: 'left' }}
        />
      )}
      <Title level={4} style={{ marginBottom: 4 }}>
        評估結論
      </Title>
      <div style={{ margin: '16px 0' }}>
        <StatusBadge status={report.final_status} large />
      </div>
      <Text type="secondary">{report.final_status_text}</Text>
      <div style={{ marginTop: 12 }}>
        <Text>案件編號：{report.project_id}</Text>
        <br />
        <Text type="secondary">規則版本：{report.rule_version}</Text>
        <br />
        <Text type="secondary">
          產出時間：{new Date(report.generated_at).toLocaleString('zh-TW')}
        </Text>
      </div>
      {report.blockers.length > 0 && (
        <div style={{ marginTop: 16, textAlign: 'left' }}>
          <Text strong type="danger">不通過項目（Blocker）：</Text>
          <ul style={{ paddingLeft: 20, marginTop: 4 }}>
            {report.blockers.map((item, i) => (
              <li key={i}>
                <Text type="danger">{item}</Text>
              </li>
            ))}
          </ul>
        </div>
      )}
      {report.high_risk_items.length > 0 && (
        <div style={{ marginTop: 16, textAlign: 'left' }}>
          <Text strong style={{ color: '#722ed1' }}>高風險項目：</Text>
          <ul style={{ paddingLeft: 20, marginTop: 4 }}>
            {report.high_risk_items.map((item, i) => (
              <li key={i}>
                <Text style={{ color: '#722ed1' }}>{item}</Text>
              </li>
            ))}
          </ul>
        </div>
      )}
      {report.manual_review_items.length > 0 && (
        <div style={{ marginTop: 16, textAlign: 'left' }}>
          <Text strong type="warning">需人工覆核項目：</Text>
          <ul style={{ paddingLeft: 20, marginTop: 4 }}>
            {report.manual_review_items.map((item, i) => (
              <li key={i}>
                <Text type="warning">{item}</Text>
              </li>
            ))}
          </ul>
        </div>
      )}
    </Card>
  )
}

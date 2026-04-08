import { Layout, Typography, Button, Divider, Empty } from 'antd'
import { useLocation, useNavigate } from 'react-router-dom'
import type { EvaluationReport } from '../types'
import ReportSummary from '../components/ReportSummary'
import Checklist19 from '../components/Checklist19'
import ChecklistDetailCards from '../components/ChecklistDetailCards'
import OverlayRiskList from '../components/OverlayRiskList'
import EvidenceTable from '../components/EvidenceTable'

const { Header, Content } = Layout
const { Title } = Typography

export default function ResultPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const report = (location.state as { report?: EvaluationReport })?.report

  if (!report) {
    return (
      <Layout style={{ minHeight: '100vh', background: '#f5f5f5' }}>
        <Content style={{ padding: 40, textAlign: 'center' }}>
          <Empty description="尚無評估結果" />
          <Button type="primary" onClick={() => navigate('/')} style={{ marginTop: 16 }}>
            返回輸入
          </Button>
        </Content>
      </Layout>
    )
  }

  return (
    <Layout style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Header style={{ background: '#001529', display: 'flex', alignItems: 'center' }}>
        <Title level={3} style={{ color: '#fff', margin: 0 }}>
          評估報告
        </Title>
      </Header>
      <Content style={{ padding: '24px 40px', maxWidth: 960, margin: '0 auto', width: '100%' }}>
        <ReportSummary report={report} />

        <Divider>19 點法規評估總覽</Divider>
        <Checklist19 items={report.checklist_19} />

        {report.overlay_risks.length > 0 && (
          <>
            <Divider>疊圖風險</Divider>
            <OverlayRiskList risks={report.overlay_risks} />
          </>
        )}

        <Divider>各點詳細判定</Divider>
        <ChecklistDetailCards items={report.checklist_19} />

        <Divider>法規依據</Divider>
        <EvidenceTable data={report.legal_basis} />

        <div style={{ textAlign: 'center', margin: '32px 0' }}>
          <Button type="primary" onClick={() => navigate('/')}>
            重新評估
          </Button>
        </div>
      </Content>
    </Layout>
  )
}

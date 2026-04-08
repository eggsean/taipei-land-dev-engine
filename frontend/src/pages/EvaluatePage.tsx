import { Layout, Typography, message } from 'antd'
import { useNavigate } from 'react-router-dom'
import SiteInputForm from '../components/SiteInputForm'
import { useEvaluate } from '../hooks/useEvaluate'
import type { SiteInput } from '../types'

const { Header, Content } = Layout
const { Title } = Typography

export default function EvaluatePage() {
  const navigate = useNavigate()
  const mutation = useEvaluate()

  const handleSubmit = (values: SiteInput) => {
    mutation.mutate(values, {
      onSuccess: (report) => {
        navigate('/result', { state: { report } })
      },
      onError: (err) => {
        message.error('評估失敗：' + (err instanceof Error ? err.message : '未知錯誤'))
      },
    })
  }

  return (
    <Layout style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Header style={{ background: '#001529', display: 'flex', alignItems: 'center' }}>
        <Title level={3} style={{ color: '#fff', margin: 0 }}>
          臺北市土地開發法定結論系統
        </Title>
      </Header>
      <Content style={{ padding: '40px', maxWidth: 640, margin: '0 auto', width: '100%' }}>
        <SiteInputForm onSubmit={handleSubmit} loading={mutation.isPending} />
      </Content>
    </Layout>
  )
}

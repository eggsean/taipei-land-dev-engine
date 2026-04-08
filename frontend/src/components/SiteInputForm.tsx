import { Button, Form, Input, InputNumber, Select, Switch, Card, Typography } from 'antd'
import type { SiteInput } from '../types'

const { Title } = Typography

const useOptions = [
  { value: 'residential', label: '住宅' },
  { value: 'office', label: '辦公' },
  { value: 'commercial', label: '商業' },
  { value: 'hotel', label: '旅館' },
  { value: 'industrial_office', label: '廠辦' },
]

const schemeOptions = [
  { value: 'general', label: '一般開發' },
  { value: 'urban_renewal', label: '都市更新' },
  { value: 'dangerous_old', label: '危老重建' },
]

interface Props {
  onSubmit: (values: SiteInput) => void
  loading: boolean
}

export default function SiteInputForm({ onSubmit, loading }: Props) {
  const [form] = Form.useForm()

  return (
    <Card>
      <Title level={4}>基地資料輸入</Title>
      <Form
        form={form}
        layout="vertical"
        onFinish={onSubmit}
        initialValues={{ intended_use: 'residential' }}
      >
        <Form.Item
          name="address_or_lot"
          label="地址或地號"
          rules={[{ required: true, message: '請輸入地址或地號' }]}
        >
          <Input placeholder="例：臺北市大安區仁愛路三段1號" />
        </Form.Item>

        <Form.Item
          name="site_area_sqm"
          label="基地面積（平方公尺）"
          extra="不填則系統自動從地籍資料查詢"
        >
          <InputNumber min={1} style={{ width: '100%' }} placeholder="選填，自動查詢" />
        </Form.Item>

        <Form.Item
          name="intended_use"
          label="預計用途"
          rules={[{ required: true, message: '請選擇用途' }]}
        >
          <Select options={useOptions} />
        </Form.Item>

        <Form.Item name="development_scheme" label="預計制度（選填）">
          <Select options={schemeOptions} allowClear placeholder="選填" />
        </Form.Item>

        <Form.Item name="single_owner" label="單一地主" valuePropName="checked">
          <Switch />
        </Form.Item>

        <Form.Item name="has_existing_building" label="已有建物" valuePropName="checked">
          <Switch />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block size="large">
            開始法規初判
          </Button>
        </Form.Item>
      </Form>
    </Card>
  )
}

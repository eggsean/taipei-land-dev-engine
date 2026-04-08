import { Table, Tag } from 'antd'
import type { LegalBasis } from '../types'

const columns = [
  { title: '法規名稱', dataIndex: 'law_name', key: 'law_name' },
  { title: '條次', dataIndex: 'article', key: 'article' },
  {
    title: '來源類型',
    dataIndex: 'source_type',
    key: 'source_type',
    render: (t: string) => {
      const labels: Record<string, string> = {
        central_law: '中央法',
        local_law: '地方法',
        gis_data: '圖資',
        system_query: '系統查詢',
      }
      return <Tag>{labels[t] || t}</Tag>
    },
  },
  {
    title: '來源',
    dataIndex: 'source_url',
    key: 'source_url',
    render: (url: string) =>
      url ? (
        <a href={url} target="_blank" rel="noreferrer">
          連結
        </a>
      ) : (
        '-'
      ),
  },
  {
    title: '需覆核',
    dataIndex: 'review_required',
    key: 'review_required',
    render: (v: boolean) => (v ? <Tag color="warning">是</Tag> : <Tag color="default">否</Tag>),
  },
]

export default function EvidenceTable({ data }: { data: LegalBasis[] }) {
  return (
    <Table
      columns={columns}
      dataSource={data.map((d, i) => ({ ...d, key: i }))}
      size="small"
      pagination={false}
      style={{ marginTop: 16 }}
    />
  )
}

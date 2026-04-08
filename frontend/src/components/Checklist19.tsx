import { Table, Tag, Tooltip } from 'antd'
import type { ChecklistItem, FinalStatus } from '../types'
import StatusBadge from './StatusBadge'

const columns = [
  {
    title: '#',
    dataIndex: 'point_number',
    key: 'point_number',
    width: 50,
  },
  {
    title: '評估項目',
    dataIndex: 'title',
    key: 'title',
  },
  {
    title: '範圍',
    dataIndex: 'v1_scope',
    key: 'v1_scope',
    width: 80,
    render: (v: boolean) => (v ? <Tag color="blue">V1</Tag> : <Tag>V2</Tag>),
  },
  {
    title: '判定結果',
    dataIndex: 'status',
    key: 'status',
    width: 130,
    render: (status: FinalStatus | null, record: ChecklistItem) =>
      status ? <StatusBadge status={status} /> : <Tag>{record.status_text}</Tag>,
  },
  {
    title: '說明',
    dataIndex: 'status_text',
    key: 'status_text',
    ellipsis: true,
    render: (text: string, record: ChecklistItem) => (
      <Tooltip title={record.notes.join('; ')}>
        <span>{text}</span>
      </Tooltip>
    ),
  },
]

export default function Checklist19({ items }: { items: ChecklistItem[] }) {
  return (
    <Table
      columns={columns}
      dataSource={items.map((d) => ({ ...d, key: d.point_number }))}
      size="small"
      pagination={false}
      rowClassName={(record) => (!record.v1_scope ? 'checklist-v2-row' : '')}
    />
  )
}

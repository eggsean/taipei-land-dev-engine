import { Tag } from 'antd'
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
  WarningOutlined,
} from '@ant-design/icons'
import type { FinalStatus } from '../types'

const config: Record<FinalStatus, { color: string; label: string; icon: React.ReactNode }> = {
  AUTO_PASS: { color: 'success', label: '可初步開發', icon: <CheckCircleOutlined /> },
  AUTO_FAIL: { color: 'error', label: '不建議取得', icon: <CloseCircleOutlined /> },
  REVIEW_REQUIRED: { color: 'warning', label: '需人工判定', icon: <ExclamationCircleOutlined /> },
  HIGH_RISK: { color: 'purple', label: '高風險', icon: <WarningOutlined /> },
}

export default function StatusBadge({ status, large }: { status: FinalStatus; large?: boolean }) {
  const c = config[status]
  return (
    <Tag
      icon={c.icon}
      color={c.color}
      style={large ? { fontSize: 18, padding: '6px 16px' } : undefined}
    >
      {c.label}
    </Tag>
  )
}

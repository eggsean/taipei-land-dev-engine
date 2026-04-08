import axios from 'axios'
import type { SiteInput, EvaluationReport } from '../types'

const api = axios.create({ baseURL: '/api/v1' })

export async function evaluateSite(input: SiteInput): Promise<EvaluationReport> {
  const { data } = await api.post<EvaluationReport>('/evaluate', input)
  return data
}

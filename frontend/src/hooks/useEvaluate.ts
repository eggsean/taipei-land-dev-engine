import { useMutation } from '@tanstack/react-query'
import { evaluateSite } from '../api/client'
import type { SiteInput } from '../types'

export function useEvaluate() {
  return useMutation({
    mutationFn: (input: SiteInput) => evaluateSite(input),
  })
}

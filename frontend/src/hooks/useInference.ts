import { queryOptions, useSuspenseQuery } from "@tanstack/react-query"

import { InferenceService } from "@/services"

export const inferenceKeys = {
  all: ["inference"] as const,
  prediction: (symbol: string) =>
    [...inferenceKeys.all, "prediction", symbol] as const,
}

export function predictionQueryOptions(symbol: string) {
  return queryOptions({
    queryKey: inferenceKeys.prediction(symbol),
    queryFn: () => InferenceService.predictStock(symbol),
    staleTime: 2 * 60 * 1000,
  })
}

export function usePrediction(symbol: string) {
  return useSuspenseQuery(predictionQueryOptions(symbol))
}

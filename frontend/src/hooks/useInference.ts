import { useMutation } from "@tanstack/react-query"

import { InferenceService } from "@/services"
import type { PredictionRequest } from "@/types"

export function usePrediction() {
  return useMutation({
    mutationFn: (request: PredictionRequest) =>
      InferenceService.predict(request),
  })
}

export type PredictionHorizon = "1h" | "4h" | "1d" | "1w"

export interface PredictionRequest {
  symbol: string
  horizon: PredictionHorizon
  features_override?: Record<string, unknown> | null
}

export interface PredictionResponse {
  symbol: string
  prediction: number
  confidence: number
  model_version: string
  predicted_at: string
  prediction_target_time: number
}

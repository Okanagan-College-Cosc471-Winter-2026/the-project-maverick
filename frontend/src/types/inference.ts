export type PredictionHorizon = "1h" | "4h" | "1d" | "1w"

export interface PredictionRequest {
  symbol: string
  horizon: PredictionHorizon
  features_override?: Record<string, unknown> | null
}

export interface PredictionResponse {
  symbol: string
  current_price: number
  predicted_price: number
  predicted_return: number
  prediction_date: string
  confidence: number | null
  model_version: string
}

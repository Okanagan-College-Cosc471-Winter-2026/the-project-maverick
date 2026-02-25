export interface PredictionResponse {
  symbol: string
  current_price: number
  predicted_price: number
  predicted_return: number
  prediction_date: string
  confidence: number | null
  model_version: string
}

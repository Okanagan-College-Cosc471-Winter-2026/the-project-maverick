import type { CancelablePromise } from "@/client/core/CancelablePromise"
import { OpenAPI } from "@/client/core/OpenAPI"
import { request as __request } from "@/client/core/request"
import type { PredictionRequest, PredictionResponse } from "@/types"

export class InferenceService {
  /**
   * Get prediction for a stock.
   * @param symbol Stock symbol (e.g., 'AAPL')
   * @returns PredictionResponse Successful Response
   * @throws ApiError
   */
  public static predictStock(
    symbol: string,
  ): CancelablePromise<PredictionResponse> {
    return __request(OpenAPI, {
      method: "GET",
      url: `/api/v1/inference/predict/${symbol}`,
      errors: {
        404: "Stock not found",
        400: "Insufficient data",
        422: "Validation Error",
      },
    })
  }

  // Legacy method for backwards compatibility
  public static predict(
    requestBody: PredictionRequest,
  ): CancelablePromise<PredictionResponse> {
    return InferenceService.predictStock(requestBody.symbol)
  }
}

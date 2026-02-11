import type { CancelablePromise } from "@/client/core/CancelablePromise"
import { OpenAPI } from "@/client/core/OpenAPI"
import { request as __request } from "@/client/core/request"
import type { PredictionRequest, PredictionResponse } from "@/types"

export class InferenceService {
  /**
   * Get prediction for a stock.
   * @param requestBody Prediction request payload
   * @returns PredictionResponse Successful Response
   * @throws ApiError
   */
  public static predict(
    requestBody: PredictionRequest,
  ): CancelablePromise<PredictionResponse> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/inference/predict",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: "Validation Error",
      },
    })
  }
}

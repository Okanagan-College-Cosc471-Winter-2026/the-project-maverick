import type { CancelablePromise } from "@/client/core/CancelablePromise"
import { OpenAPI } from "@/client/core/OpenAPI"
import { request as __request } from "@/client/core/request"
import type { OHLCRead, StockRead } from "@/types"

export class MarketService {
  /**
   * List all active stocks.
   * @returns StockRead[] Successful Response
   * @throws ApiError
   */
  public static listStocks(): CancelablePromise<StockRead[]> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/market/stocks",
    })
  }

  /**
   * Get metadata for a single stock.
   * @param symbol Stock ticker symbol
   * @returns StockRead Successful Response
   * @throws ApiError
   */
  public static getStock(symbol: string): CancelablePromise<StockRead> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/market/stocks/{symbol}",
      path: {
        symbol,
      },
      errors: {
        404: "Stock not found",
      },
    })
  }

  /**
   * Get daily OHLC + volume data for a stock.
   * @param symbol Stock ticker symbol
   * @param days Number of calendar days to look back (default 365)
   * @returns OHLCRead[] Successful Response
   * @throws ApiError
   */
  public static getOHLC(
    symbol: string,
    days: number = 365,
  ): CancelablePromise<OHLCRead[]> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/market/stocks/{symbol}/ohlc",
      path: {
        symbol,
      },
      query: {
        days,
      },
      errors: {
        404: "Stock not found",
      },
    })
  }
}

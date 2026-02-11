import { queryOptions, useSuspenseQuery } from "@tanstack/react-query"

import { MarketService } from "@/services"

export const marketKeys = {
  all: ["market"] as const,
  stocks: () => [...marketKeys.all, "stocks"] as const,
  stock: (symbol: string) => [...marketKeys.all, "stock", symbol] as const,
  ohlc: (symbol: string, days: number) =>
    [...marketKeys.all, "ohlc", symbol, days] as const,
}

export function stocksQueryOptions() {
  return queryOptions({
    queryKey: marketKeys.stocks(),
    queryFn: () => MarketService.listStocks(),
    staleTime: 5 * 60 * 1000,
  })
}

export function stockQueryOptions(symbol: string) {
  return queryOptions({
    queryKey: marketKeys.stock(symbol),
    queryFn: () => MarketService.getStock(symbol),
    staleTime: 5 * 60 * 1000,
  })
}

export function ohlcQueryOptions(symbol: string, days: number = 365) {
  return queryOptions({
    queryKey: marketKeys.ohlc(symbol, days),
    queryFn: () => MarketService.getOHLC(symbol, days),
    staleTime: 1 * 60 * 1000,
  })
}

export function useStocks() {
  return useSuspenseQuery(stocksQueryOptions())
}

export function useStock(symbol: string) {
  return useSuspenseQuery(stockQueryOptions(symbol))
}

export function useOHLC(symbol: string, days: number = 365) {
  return useSuspenseQuery(ohlcQueryOptions(symbol, days))
}

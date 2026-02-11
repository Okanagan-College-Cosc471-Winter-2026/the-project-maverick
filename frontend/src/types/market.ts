export interface StockRead {
  symbol: string
  name: string
  sector: string | null
  industry: string | null
  exchange: string | null
}

export interface OHLCRead {
  time: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

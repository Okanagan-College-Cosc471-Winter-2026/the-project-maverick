import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import { ArrowLeft } from "lucide-react"
import { Suspense, useState } from "react"
import { PredictionForm } from "@/components/Stocks/PredictionForm"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ohlcQueryOptions, stockQueryOptions } from "@/hooks/useMarket"
import { StockChart } from "@/components/Charts/StockChart"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"

export const Route = createFileRoute("/dashboard/stocks/$symbol")({
  component: StockDetail,
  head: ({ params }) => ({
    meta: [
      {
        title: `${params.symbol} - Stock Prediction`,
      },
    ],
  }),
})

function StockHeader({ symbol }: { symbol: string }) {
  const { data: stock } = useSuspenseQuery(stockQueryOptions(symbol))

  return (
    <div className="flex items-center gap-4">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          {stock.name}{" "}
          <span className="font-mono text-muted-foreground">
            ({stock.symbol})
          </span>
        </h1>
        <div className="flex items-center gap-2 mt-1">
          {stock.sector && <Badge variant="secondary">{stock.sector}</Badge>}
          {stock.industry && <Badge variant="outline">{stock.industry}</Badge>}
          {stock.exchange && (
            <span className="text-sm text-muted-foreground">
              {stock.exchange}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

function ChartTab({ symbol }: { symbol: string }) {
  const { data: ohlc } = useSuspenseQuery(ohlcQueryOptions(symbol))
  const { data: stock } = useSuspenseQuery(stockQueryOptions(symbol))
  const [showPrediction, setShowPrediction] = useState(false)

  // Prepare data for chart
  const chartData = ohlc.map((item) => ({
    time: item.time as any,
    open: item.open,
    high: item.high,
    low: item.low,
    close: item.close,
  }))

  const lastPrice = ohlc[ohlc.length - 1]?.close || 0
  const previousPrice = ohlc[ohlc.length - 2]?.close || 0
  const priceChange = lastPrice - previousPrice
  const priceChangePercent = (priceChange / previousPrice) * 100

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-xl mb-1">
              {stock.name} ({stock.symbol})
            </CardTitle>
            <CardDescription>Historical OHLC data</CardDescription>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <div className="text-xs text-muted-foreground">Current Price</div>
              <div className="text-lg font-bold">${lastPrice.toFixed(2)}</div>
              <div className={`text-xs ${priceChange >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)} ({priceChangePercent.toFixed(2)}%)
              </div>
            </div>

            <div className="h-10 w-px bg-border" />

            <div className="text-right">
              <div className="text-xs text-muted-foreground">Volume</div>
              <div className="text-lg font-bold">{(ohlc[ohlc.length - 1]?.volume ?? 0).toLocaleString()}</div>
              <div className="text-xs text-muted-foreground">Latest trading</div>
            </div>

            <div className="h-10 w-px bg-border" />

            <div className="flex items-center space-x-2">
              <Switch
                id="prediction-mode"
                checked={showPrediction}
                onCheckedChange={setShowPrediction}
                disabled={true}
              />
              <Label htmlFor="prediction-mode" className="text-xs whitespace-nowrap">
                Show Prediction
              </Label>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pl-2">
        <div className="h-[500px] w-full">
          <StockChart data={chartData} />
        </div>
      </CardContent>
    </Card>
  )
}

function DetailsTab({ symbol }: { symbol: string }) {
  const { data: stock } = useSuspenseQuery(stockQueryOptions(symbol))

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Stock Information</CardTitle>
      </CardHeader>
      <CardContent>
        <dl className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <dt className="text-muted-foreground">Symbol</dt>
            <dd className="font-mono font-medium">{stock.symbol}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Name</dt>
            <dd className="font-medium">{stock.name}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Sector</dt>
            <dd>{stock.sector ?? "N/A"}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Industry</dt>
            <dd>{stock.industry ?? "N/A"}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Exchange</dt>
            <dd>{stock.exchange ?? "N/A"}</dd>
          </div>
        </dl>
      </CardContent>
    </Card>
  )
}

function LoadingFallback() {
  return (
    <div className="flex flex-col gap-4">
      <Skeleton className="h-8 w-64" />
      <Skeleton className="h-64 w-full" />
    </div>
  )
}

function StockDetail() {
  const { symbol } = Route.useParams()

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link to="/dashboard/stocks">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <Suspense fallback={<Skeleton className="h-10 w-64" />}>
          <StockHeader symbol={symbol} />
        </Suspense>
      </div>

      <Tabs defaultValue="chart">
        <TabsList>
          <TabsTrigger value="chart">Chart</TabsTrigger>
          <TabsTrigger value="prediction">Prediction</TabsTrigger>
          <TabsTrigger value="details">Details</TabsTrigger>
        </TabsList>
        <TabsContent value="chart">
          <Suspense fallback={<LoadingFallback />}>
            <ChartTab symbol={symbol} />
          </Suspense>
        </TabsContent>
        <TabsContent value="prediction">
          <PredictionForm symbol={symbol} />
        </TabsContent>
        <TabsContent value="details">
          <Suspense fallback={<LoadingFallback />}>
            <DetailsTab symbol={symbol} />
          </Suspense>
        </TabsContent>
      </Tabs>
    </div>
  )
}

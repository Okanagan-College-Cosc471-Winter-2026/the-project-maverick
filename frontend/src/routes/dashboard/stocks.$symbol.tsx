import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import { ArrowLeft, BarChart3, LineChart } from "lucide-react"
import { Suspense, useState } from "react"
import { type ChartType, StockChart } from "@/components/Charts/StockChart"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Skeleton } from "@/components/ui/skeleton"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ohlcQueryOptions, stockQueryOptions } from "@/hooks/useMarket"
import { InferenceService } from "@/services"

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
  const [chartType, setChartType] = useState<ChartType>("line")
  const [prediction, setPrediction] = useState<any>(null)
  const [loadingPrediction, setLoadingPrediction] = useState(false)
  const [timeRange, setTimeRange] = useState<"1D" | "1W" | "1M" | "ALL">("ALL")

  // Filter data based on time range
  const getFilteredData = () => {
    const now = Date.now() / 1000 // Current time in Unix timestamp
    const oneDayAgo = now - 24 * 60 * 60
    const oneWeekAgo = now - 7 * 24 * 60 * 60
    const onMonthAgo = now - 30 * 24 * 60 * 60

    switch (timeRange) {
      case "1D":
        return ohlc.filter((item) => item.time >= oneDayAgo)
      case "1W":
        return ohlc.filter((item) => item.time >= oneWeekAgo)
      case "1M":
        return ohlc.filter((item) => item.time >= onMonthAgo)
      default:
        return ohlc
    }
  }

  const filteredOhlc = getFilteredData()

  // Prepare data for chart
  const chartData = filteredOhlc.map((item) => ({
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

  // Load prediction when toggle is enabled
  const handlePredictionToggle = async (checked: boolean) => {
    setShowPrediction(checked)
    if (checked && !prediction) {
      setLoadingPrediction(true)
      try {
        const result = await InferenceService.predictStock(symbol)
        setTimeRange("1W")
        setPrediction(result)
      } catch (error) {
        console.error("Failed to load prediction:", error)
        setShowPrediction(false)
      } finally {
        setLoadingPrediction(false)
      }
    }
  }

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
              <div
                className={`text-xs ${priceChange >= 0 ? "text-green-500" : "text-red-500"}`}
              >
                {priceChange >= 0 ? "+" : ""}
                {priceChange.toFixed(2)} ({priceChangePercent.toFixed(2)}%)
              </div>
            </div>

            {showPrediction && prediction && (
              <>
                <div className="h-10 w-px bg-border" />
                <div className="text-right">
                  <div className="text-xs text-muted-foreground">
                    Predicted (60d)
                  </div>
                  <div className="text-lg font-bold">
                    ${prediction.predicted_price.toFixed(2)}
                  </div>
                  <div
                    className={`text-xs ${prediction.predicted_return >= 0 ? "text-green-500" : "text-red-500"}`}
                  >
                    {prediction.predicted_return >= 0 ? "+" : ""}
                    {prediction.predicted_return.toFixed(2)}%
                  </div>
                </div>
              </>
            )}

            <div className="h-10 w-px bg-border" />

            <div className="text-right">
              <div className="text-xs text-muted-foreground">Volume</div>
              <div className="text-lg font-bold">
                {(ohlc[ohlc.length - 1]?.volume ?? 0).toLocaleString()}
              </div>
              <div className="text-xs text-muted-foreground">
                Latest trading
              </div>
            </div>

            <div className="h-10 w-px bg-border" />

            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <Button
                  variant={chartType === "candlestick" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setChartType("candlestick")}
                >
                  <BarChart3 className="h-4 w-4" />
                </Button>
                <Button
                  variant={chartType === "line" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setChartType("line")}
                >
                  <LineChart className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex items-center gap-1">
                <Button
                  variant={timeRange === "1D" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setTimeRange("1D")}
                  className="text-xs px-2"
                >
                  1D
                </Button>
                <Button
                  variant={timeRange === "1W" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setTimeRange("1W")}
                  className="text-xs px-2"
                >
                  1W
                </Button>
                <Button
                  variant={timeRange === "1M" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setTimeRange("1M")}
                  className="text-xs px-2"
                >
                  1M
                </Button>

                <Button
                  variant={timeRange === "ALL" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setTimeRange("ALL")}
                  className="text-xs px-2"
                >
                  All
                </Button>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="prediction-mode"
                  checked={showPrediction}
                  onCheckedChange={handlePredictionToggle}
                  disabled={loadingPrediction}
                />
                <Label
                  htmlFor="prediction-mode"
                  className="text-xs whitespace-nowrap"
                >
                  {loadingPrediction ? "Loading..." : "Show Prediction"}
                </Label>
              </div>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pl-2">
        <div className="h-[500px] w-full">
          <StockChart
            data={chartData}
            chartType={chartType}
            predictionPrice={
              showPrediction && prediction
                ? prediction.predicted_price
                : undefined
            }
            predictionDate={
              showPrediction && prediction
                ? prediction.prediction_date
                : undefined
            }
          />
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
          <TabsTrigger value="details">Details</TabsTrigger>
        </TabsList>
        <TabsContent value="chart">
          <Suspense fallback={<LoadingFallback />}>
            <ChartTab symbol={symbol} />
          </Suspense>
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

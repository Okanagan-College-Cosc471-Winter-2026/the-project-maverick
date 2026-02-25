import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import {
  ArrowDownRight,
  ArrowUpRight,
  Loader2,
  TrendingUp,
} from "lucide-react"
import { Suspense, useState } from "react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { stocksQueryOptions } from "@/hooks/useMarket"
import { InferenceService } from "@/services"
import type { PredictionResponse } from "@/types"

export const Route = createFileRoute("/dashboard/predictions")({
  component: Predictions,
  head: () => ({
    meta: [
      {
        title: "Predictions - Stock Prediction",
      },
    ],
  }),
})

function PredictionCard({ prediction }: { prediction: PredictionResponse }) {
  const isPositive = prediction.predicted_return >= 0

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-mono">
            {prediction.symbol}
          </CardTitle>
          <Badge variant={isPositive ? "default" : "destructive"}>
            {isPositive ? (
              <ArrowUpRight className="h-3 w-3 mr-1" />
            ) : (
              <ArrowDownRight className="h-3 w-3 mr-1" />
            )}
            {isPositive ? "+" : ""}
            {prediction.predicted_return.toFixed(2)}%
          </Badge>
        </div>
        <CardDescription>
          {new Date(prediction.prediction_date).toLocaleDateString()}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <dl className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <dt className="text-muted-foreground">Current</dt>
            <dd className="font-bold text-lg">
              ${prediction.current_price.toFixed(2)}
            </dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Predicted</dt>
            <dd
              className={`font-bold text-lg ${isPositive ? "text-green-500" : "text-red-500"}`}
            >
              ${prediction.predicted_price.toFixed(2)}
            </dd>
          </div>
          {prediction.confidence != null && (
            <div>
              <dt className="text-muted-foreground">Confidence</dt>
              <dd className="font-semibold">
                {(prediction.confidence * 100).toFixed(0)}%
              </dd>
            </div>
          )}
          <div>
            <dt className="text-muted-foreground">Model</dt>
            <dd className="font-mono text-xs">{prediction.model_version}</dd>
          </div>
        </dl>
        <div className="mt-4">
          <Button variant="outline" size="sm" asChild className="w-full">
            <Link
              to="/dashboard/stocks/$symbol"
              params={{ symbol: prediction.symbol }}
            >
              View Chart
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

function PredictionsContent() {
  const { data: stocks } = useSuspenseQuery(stocksQueryOptions())
  const [selectedSymbol, setSelectedSymbol] = useState("")
  const [predictions, setPredictions] = useState<PredictionResponse[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handlePredict = async () => {
    if (!selectedSymbol) return
    setLoading(true)
    setError(null)
    try {
      const result = await InferenceService.predictStock(selectedSymbol)
      setPredictions((prev) => {
        const filtered = prev.filter((p) => p.symbol !== result.symbol)
        return [result, ...filtered]
      })
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to generate prediction",
      )
    } finally {
      setLoading(false)
    }
  }

  const handlePredictAll = async () => {
    setLoading(true)
    setError(null)
    try {
      const results = await Promise.allSettled(
        stocks.map((s) => InferenceService.predictStock(s.symbol)),
      )
      const successful = results
        .filter(
          (r): r is PromiseFulfilledResult<PredictionResponse> =>
            r.status === "fulfilled",
        )
        .map((r) => r.value)
      setPredictions(successful)
    } catch (err) {
      setError("Failed to generate predictions")
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Generate Prediction</CardTitle>
          <CardDescription>
            Select a stock to generate a price prediction
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-3">
            <Select value={selectedSymbol} onValueChange={setSelectedSymbol}>
              <SelectTrigger className="w-64">
                <SelectValue placeholder="Select a stock..." />
              </SelectTrigger>
              <SelectContent>
                {stocks.map((stock) => (
                  <SelectItem key={stock.symbol} value={stock.symbol}>
                    {stock.symbol} — {stock.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button
              onClick={handlePredict}
              disabled={!selectedSymbol || loading}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <TrendingUp className="h-4 w-4 mr-2" />
              )}
              Predict
            </Button>
            <Button
              variant="outline"
              onClick={handlePredictAll}
              disabled={loading}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : null}
              Predict All
            </Button>
          </div>
          {error && (
            <p className="text-sm text-red-500 mt-2">{error}</p>
          )}
        </CardContent>
      </Card>

      {predictions.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {predictions.map((prediction) => (
            <PredictionCard
              key={prediction.symbol}
              prediction={prediction}
            />
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center text-center py-12">
          <div className="rounded-full bg-muted p-4 mb-4">
            <TrendingUp className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-semibold">No predictions yet</h3>
          <p className="text-muted-foreground">
            Select a stock above to generate a prediction
          </p>
        </div>
      )}
    </>
  )
}

function Predictions() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Predictions</h1>
        <p className="text-muted-foreground">
          View and manage stock predictions
        </p>
      </div>
      <Suspense
        fallback={
          <div className="flex flex-col gap-4">
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-64 w-full" />
          </div>
        }
      >
        <PredictionsContent />
      </Suspense>
    </div>
  )
}

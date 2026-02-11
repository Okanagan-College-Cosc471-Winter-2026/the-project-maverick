import { createFileRoute, Link } from "@tanstack/react-router"
import { TrendingUp } from "lucide-react"

import { Button } from "@/components/ui/button"

export const Route = createFileRoute("/_layout/predictions")({
  component: Predictions,
  head: () => ({
    meta: [
      {
        title: "Predictions - Stock Prediction",
      },
    ],
  }),
})

function Predictions() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Predictions</h1>
        <p className="text-muted-foreground">
          View and manage stock predictions
        </p>
      </div>
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <TrendingUp className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">No predictions yet</h3>
        <p className="text-muted-foreground mb-4">
          Navigate to a stock detail page to generate a prediction
        </p>
        <Button asChild>
          <Link to="/stocks">Browse Stocks</Link>
        </Button>
      </div>
    </div>
  )
}

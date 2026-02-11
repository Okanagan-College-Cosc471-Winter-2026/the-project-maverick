import { createFileRoute, Link } from "@tanstack/react-router"
import { ArrowRight, BarChart2, Calendar, Cpu, LineChart } from "lucide-react"
import { Button } from "@/components/ui/button"

export const Route = createFileRoute("/")({
  component: Welcome,
})

function Welcome() {
  return (
    <div className="flex min-h-screen w-full flex-col bg-background">
      {/* Hero Section */}
      <div className="flex flex-1 flex-col items-center justify-center px-4 text-center pt-20 pb-16">
        <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
          <BarChart2 className="h-8 w-8 text-primary" />
        </div>

        <h1 className="mb-4 text-4xl font-extrabold tracking-tight lg:text-6xl">
          Welcome to MarketSight 📈
        </h1>

        <p className="mb-8 max-w-[800px] text-lg text-muted-foreground lg:text-xl">
          Unlock clearer insights into the financial markets with{" "}
          <strong>MarketSight</strong> — your all-in-one platform for analyzing
          historical market data, visualizing trends, and forecasting future
          price movements.
        </p>

        <div className="flex gap-4">
          <Button asChild size="lg" className="h-12 px-8 text-base">
            <Link to="/dashboard">
              Start exploring
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </div>

      {/* Features Grid */}
      <div className="container mx-auto px-4 pb-24">
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          <div className="rounded-xl border bg-card p-6 shadow-sm">
            <LineChart className="mb-4 h-8 w-8 text-primary" />
            <h3 className="mb-2 text-lg font-bold">Historical Data</h3>
            <p className="text-muted-foreground">
              Explore historical price data across stocks, indexes, and
              commodities with interactive charts.
            </p>
          </div>

          <div className="rounded-xl border bg-card p-6 shadow-sm">
            <Cpu className="mb-4 h-8 w-8 text-primary" />
            <h3 className="mb-2 text-lg font-bold">AI Predictions</h3>
            <p className="text-muted-foreground">
              See data-driven predictions overlaid with actual market behavior
              using our advanced models.
            </p>
          </div>

          <div className="rounded-xl border bg-card p-6 shadow-sm">
            <Calendar className="mb-4 h-8 w-8 text-primary" />
            <h3 className="mb-2 text-lg font-bold">Flexible Filtering</h3>
            <p className="text-muted-foreground">
              Filter by date, exchange, and asset type with flexible controls to
              find exactly what you need.
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t py-8 text-center text-sm text-muted-foreground">
        <div className="container flex flex-col items-center justify-between gap-4 md:flex-row">
          <p>© 2026 MarketSight. All rights reserved.</p>
          <p>
            Powered by data. Made for analysts, investors, and curious minds.
          </p>
        </div>
      </footer>
    </div>
  )
}

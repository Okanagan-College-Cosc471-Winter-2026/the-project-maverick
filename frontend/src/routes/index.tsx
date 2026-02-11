import { createFileRoute, Link } from "@tanstack/react-router"
import { Button } from "@/components/ui/button"
import { ArrowRight, BarChart2 } from "lucide-react"

export const Route = createFileRoute("/")({
  component: Welcome,
})

function Welcome() {
  return (
    <div className="flex h-screen w-full flex-col items-center justify-center bg-background px-4 text-center">
      <div className="mb-8 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
        <BarChart2 className="h-8 w-8 text-primary" />
      </div>

      <h1 className="mb-4 text-4xl font-extrabold tracking-tight lg:text-5xl">
        The Project Maverick
      </h1>

      <p className="mb-8 max-w-[600px] text-lg text-muted-foreground">
        Advanced stock market analytics and prediction platform.
        Track performance, analyze trends, and get AI-powered insights.
      </p>

      <div className="flex gap-4">
        <Button asChild size="lg" className="h-12 px-8 text-base">
          <Link to="/dashboard">
            Enter App
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </div>
    </div>
  )
}

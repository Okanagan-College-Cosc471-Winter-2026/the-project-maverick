import { LineChart } from "lucide-react"

import type { OHLCRead } from "@/types"

interface OHLCChartPlaceholderProps {
  data: OHLCRead[]
}

export function OHLCChartPlaceholder({ data }: OHLCChartPlaceholderProps) {
  const latestBar = data[data.length - 1]

  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed p-12 text-center">
      <div className="rounded-full bg-muted p-4 mb-4">
        <LineChart className="h-8 w-8 text-muted-foreground" />
      </div>
      <h3 className="text-lg font-semibold">Chart Coming Soon</h3>
      <p className="text-sm text-muted-foreground mt-1">
        {data.length} data points loaded
        {latestBar && (
          <>
            {" "}
            &middot; Latest close:{" "}
            <span className="font-mono font-medium text-foreground">
              ${latestBar.close.toFixed(2)}
            </span>
          </>
        )}
      </p>
    </div>
  )
}

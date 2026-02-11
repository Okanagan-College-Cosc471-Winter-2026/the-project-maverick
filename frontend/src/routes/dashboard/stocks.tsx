import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute, Outlet, useParams } from "@tanstack/react-router"
import { Search } from "lucide-react"
import { Suspense, useMemo, useState } from "react"

import { DataTable } from "@/components/Common/DataTable"
import PendingStocks from "@/components/Pending/PendingStocks"
import { columns } from "@/components/Stocks/columns"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { stocksQueryOptions } from "@/hooks/useMarket"

export const Route = createFileRoute("/dashboard/stocks")({
  component: Stocks,
  head: () => ({
    meta: [
      {
        title: "Stocks - MarketSight",
      },
    ],
  }),
})

function StocksTableContent({ search }: { search: string }) {
  const { data: stocks } = useSuspenseQuery(stocksQueryOptions())

  const filtered = useMemo(() => {
    if (!search) return stocks
    const q = search.toLowerCase()
    return stocks.filter(
      (s) =>
        s.symbol.toLowerCase().includes(q) || s.name.toLowerCase().includes(q),
    )
  }, [stocks, search])

  const sectors = useMemo(() => {
    const set = new Set(stocks.map((s) => s.sector).filter(Boolean))
    return Array.from(set).sort() as string[]
  }, [stocks])

  if (stocks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Search className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">No stocks available</h3>
        <p className="text-muted-foreground">
          Stock data has not been loaded yet
        </p>
      </div>
    )
  }

  return (
    <Tabs defaultValue="all">
      <TabsList>
        <TabsTrigger value="all">All Stocks</TabsTrigger>
        <TabsTrigger value="by-sector">By Sector</TabsTrigger>
      </TabsList>
      <TabsContent value="all">
        <DataTable columns={columns} data={filtered} />
      </TabsContent>
      <TabsContent value="by-sector">
        <div className="flex flex-col gap-6">
          {sectors.map((sector) => (
            <div key={sector}>
              <h3 className="text-sm font-semibold text-muted-foreground mb-2">
                {sector}
              </h3>
              <DataTable
                columns={columns}
                data={filtered.filter((s) => s.sector === sector)}
              />
            </div>
          ))}
        </div>
      </TabsContent>
    </Tabs>
  )
}

function Stocks() {
  const params = useParams({ strict: false })
  const [search, setSearch] = useState("")

  // If we have a symbol param, render the child route (stock detail page)
  if (params.symbol) {
    return <Outlet />
  }

  // Otherwise, render the stocks list
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Stocks</h1>
          <p className="text-muted-foreground">
            Browse and analyze tracked stocks
          </p>
        </div>
        <div className="relative w-64">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search stocks..."
            className="pl-8"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>
      <Suspense fallback={<PendingStocks />}>
        <StocksTableContent search={search} />
      </Suspense>
    </div>
  )
}

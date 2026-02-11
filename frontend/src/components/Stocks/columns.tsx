import { Link } from "@tanstack/react-router"
import type { ColumnDef } from "@tanstack/react-table"

import { Badge } from "@/components/ui/badge"
import type { StockRead } from "@/types"

export const columns: ColumnDef<StockRead>[] = [
  {
    accessorKey: "symbol",
    header: "Symbol",
    cell: ({ row }) => (
      <Link
        to="/dashboard/stocks/$symbol"
        params={{ symbol: row.original.symbol }}
        className="font-medium text-blue-600 hover:underline"
      >
        {row.original.symbol}
      </Link>
    ),
  },
  {
    accessorKey: "name",
    header: "Name",
    cell: ({ row }) => <span className="font-medium">{row.original.name}</span>,
  },
  {
    accessorKey: "sector",
    header: "Sector",
    cell: ({ row }) => {
      const sector = row.original.sector
      return sector ? (
        <Badge variant="secondary">{sector}</Badge>
      ) : (
        <span className="text-muted-foreground italic">N/A</span>
      )
    },
  },
  {
    accessorKey: "exchange",
    header: "Exchange",
    cell: ({ row }) => (
      <span className="text-muted-foreground">
        {row.original.exchange ?? "N/A"}
      </span>
    ),
  },
]

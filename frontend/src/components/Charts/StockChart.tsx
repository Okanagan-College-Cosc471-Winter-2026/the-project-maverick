import {
  CandlestickSeries,
  ColorType,
  createChart,
  type IChartApi,
  LineSeries,
} from "lightweight-charts"
import { useEffect, useRef } from "react"

export type ChartType = "candlestick" | "line"

export const StockChart = (props: {
  data: {
    time: string
    open: number
    high: number
    low: number
    close: number
  }[]
  chartType?: ChartType
  predictionPrice?: number
  predictionDate?: string
  colors?: {
    backgroundColor?: string
    lineColor?: string
    textColor?: string
    areaTopColor?: string
    areaBottomColor?: string
  }
}) => {
  const {
    data,
    chartType = "candlestick",
    predictionPrice,
    predictionDate,
    colors: {
      backgroundColor = "transparent",
      lineColor = "#2962FF",
      textColor = "#A1A1AA", // muted-foreground
      areaTopColor = "#2962FF",
      areaBottomColor = "rgba(41, 98, 255, 0.28)",
    } = {},
  } = props

  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)

  useEffect(() => {
    if (!chartContainerRef.current) return

    const handleResize = () => {
      chart.applyOptions({ width: chartContainerRef.current!.clientWidth })
    }

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: backgroundColor },
        textColor,
      },
      width: chartContainerRef.current.clientWidth,
      height: 400,
      grid: {
        vertLines: { color: "rgba(42, 46, 57, 0.05)" },
        horzLines: { color: "rgba(42, 46, 57, 0.05)" },
      },
    })

    chartRef.current = chart

    chart.timeScale().fitContent()

    if (chartType === "candlestick") {
      const candlestickSeries = chart.addSeries(CandlestickSeries, {
        upColor: "#26a69a",
        downColor: "#ef5350",
        borderVisible: false,
        wickUpColor: "#26a69a",
        wickDownColor: "#ef5350",
      })

      candlestickSeries.setData(data as any)

      // Add prediction line if provided
      if (predictionPrice && predictionDate) {
        const lastDataPoint = data[data.length - 1]
        // Convert ISO date to Unix timestamp (OHLC data uses timestamps)
        const predictionTimestamp = Math.floor(
          new Date(predictionDate).getTime() / 1000,
        )

        const predictionSeries = chart.addSeries(LineSeries, {
          color: "#F59E0B", // Orange color for prediction
          lineWidth: 2,
          lineStyle: 2, // Dashed line
          priceLineVisible: false,
          lastValueVisible: true,
        })

        // Draw line from last actual price to predicted price
        predictionSeries.setData([
          { time: lastDataPoint.time as any, value: lastDataPoint.close },
          { time: predictionTimestamp as any, value: predictionPrice },
        ])
      }
    } else {
      const lineSeries = chart.addSeries(LineSeries, {
        color: lineColor,
        lineWidth: 2,
      })

      // Convert OHLC to line data (using close prices)
      const lineData = data.map((d) => ({
        time: d.time as any,
        value: d.close,
      }))
      lineSeries.setData(lineData)

      // Add prediction line if provided
      if (predictionPrice && predictionDate) {
        const lastDataPoint = data[data.length - 1]
        // Convert ISO date to Unix timestamp (OHLC data uses timestamps)
        const predictionTimestamp = Math.floor(
          new Date(predictionDate).getTime() / 1000,
        )

        const predictionSeries = chart.addSeries(LineSeries, {
          color: "#F59E0B", // Orange color for prediction
          lineWidth: 3,
          lineStyle: 2, // Dashed line
          priceLineVisible: false,
          lastValueVisible: true,
        })

        // Draw line from last actual price to predicted price
        predictionSeries.setData([
          { time: lastDataPoint.time as any, value: lastDataPoint.close },
          { time: predictionTimestamp as any, value: predictionPrice },
        ])
      }
    }

    window.addEventListener("resize", handleResize)

    return () => {
      window.removeEventListener("resize", handleResize)
      chart.remove()
    }
  }, [
    data,
    chartType,
    predictionPrice,
    predictionDate,
    backgroundColor,
    lineColor,
    textColor,
  ])

  return <div ref={chartContainerRef} className="w-full relative" />
}

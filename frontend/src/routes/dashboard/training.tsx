import { createFileRoute } from "@tanstack/react-router"
import { useEffect, useRef, useState } from "react"

// ── Types ──────────────────────────────────────────────────────────────────
interface LogEntry {
  ts: string
  level: "INFO" | "WARN" | "ERROR" | "SUCCESS"
  message: string
  step: string
  progress: number
  job_id: string
  run_date: string
}

interface JobStatus {
  status: string
  job_id: string | null
  started_at: string | null
  run_date: string | null
  buffered_lines: number
}

const STEPS = ["init", "extract", "feature_eng", "hpo", "train", "save", "done"]

const LEVEL_STYLES: Record<string, string> = {
  INFO: "text-slate-300",
  WARN: "text-yellow-400",
  ERROR: "text-red-400 font-bold",
  SUCCESS: "text-emerald-400 font-semibold",
}

const STATUS_DOT: Record<string, string> = {
  idle: "bg-slate-500",
  running: "bg-yellow-400 animate-pulse",
  completed: "bg-emerald-400",
  failed: "bg-red-500",
}

// ── Route ─────────────────────────────────────────────────────────────────
// @ts-expect-error TanStack route plugin generates the route types.
export const Route = createFileRoute("/dashboard/training")({
  component: TrainingMonitor,
  head: () => ({
    meta: [{ title: "Training Monitor - MarketSight Cloud" }],
  }),
})

// ── Component ─────────────────────────────────────────────────────────────
function TrainingMonitor() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [status, setStatus] = useState<JobStatus | null>(null)
  const [connected, setConnected] = useState(false)
  const [autoScroll, setAutoScroll] = useState(true)
  const bottomRef = useRef<HTMLDivElement>(null)
  const esRef = useRef<EventSource | null>(null)

  // Calculate progress from latest log with progress field
  const latestProgress =
    [...logs].reverse().find((l) => l.progress >= 0)?.progress ?? 0

  // ── SSE connection ──────────────────────────────────────────────
  useEffect(() => {
    const connect = () => {
      const es = new EventSource("/api/v1/training/log/stream")
      esRef.current = es

      es.onopen = () => setConnected(true)
      es.onerror = () => {
        setConnected(false)
        es.close()
        setTimeout(connect, 3000) // auto-reconnect
      }
      es.onmessage = (e) => {
        try {
          const entry: LogEntry = JSON.parse(e.data)
          setLogs((prev) => [...prev.slice(-2000), entry]) // cap at 2000
        } catch {
          /* ignore malformed */
        }
      }
    }
    connect()
    return () => esRef.current?.close()
  }, [])

  // ── Poll status every 10s ───────────────────────────────────────
  useEffect(() => {
    const poll = async () => {
      try {
        const r = await fetch("/api/v1/training/status")
        if (r.ok) setStatus(await r.json())
      } catch {
        /* ignore */
      }
    }
    poll()
    const id = setInterval(poll, 10_000)
    return () => clearInterval(id)
  }, [])

  // ── Auto-scroll ─────────────────────────────────────────────────
  useEffect(() => {
    if (autoScroll) bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [autoScroll])

  // ── Helpers ─────────────────────────────────────────────────────
  const clearLogs = async () => {
    await fetch("/api/v1/training/clear", { method: "POST" })
    setLogs([])
  }

  const progressPct = Math.min(100, Math.round(latestProgress))
  const stepIdx = STEPS.indexOf(logs[logs.length - 1]?.step ?? "")

  return (
    <div className="flex h-full flex-col gap-4">
      {/* ── Header ── */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Training Monitor</h1>
          <p className="text-muted-foreground text-sm">
            Live log stream from DRAC XGBoost training jobs
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span
            className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs ${
              connected
                ? "border-emerald-500/40 text-emerald-400"
                : "border-red-500/40 text-red-400"
            }`}
          >
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                connected ? "animate-pulse bg-emerald-400" : "bg-red-400"
              }`}
            />
            {connected ? "Connected" : "Reconnecting…"}
          </span>
          <button
            type="button"
            onClick={clearLogs}
            className="rounded border border-white/10 px-3 py-1.5 text-xs text-slate-400 transition-colors hover:border-white/30 hover:text-white"
          >
            Clear
          </button>
        </div>
      </div>

      {/* ── Job status card ── */}
      {status && (
        <div className="flex flex-wrap gap-4 rounded-xl border border-white/10 bg-white/5 p-4">
          <div className="flex items-center gap-2">
            <span
              className={`h-2.5 w-2.5 rounded-full ${STATUS_DOT[status.status] ?? "bg-slate-500"}`}
            />
            <span className="text-sm font-medium capitalize">{status.status}</span>
          </div>
          {status.run_date && <Pill label="Run date" value={status.run_date} />}
          {status.job_id && <Pill label="Job ID" value={status.job_id} />}
          {status.started_at && <Pill label="Started" value={status.started_at} />}
          <Pill label="Lines" value={String(status.buffered_lines)} />
        </div>
      )}

      {/* ── Progress bar ── */}
      {(status?.status === "running" || progressPct > 0) && (
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs text-slate-400">
            <span>Progress</span>
            <span>{progressPct}%</span>
          </div>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/10">
            <div
              className="h-full rounded-full bg-emerald-500 transition-all duration-700"
              style={{ width: `${progressPct}%` }}
            />
          </div>
          {/* Step pills */}
          <div className="flex flex-wrap gap-1.5 pt-1">
            {STEPS.map((s, i) => (
              <span
                key={s}
                className={`rounded-full border px-2 py-0.5 text-[10px] transition-colors ${
                  i < stepIdx
                    ? "border-emerald-500/30 bg-emerald-500/20 text-emerald-400"
                    : i === stepIdx
                      ? "animate-pulse border-yellow-500/40 bg-yellow-500/20 text-yellow-400"
                      : "border-white/10 bg-white/5 text-slate-500"
                }`}
              >
                {s}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* ── Terminal ── */}
      <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-xl border border-white/10 bg-[#0d0d0f]">
        {/* Terminal title bar */}
        <div className="flex items-center gap-2 border-b border-white/10 bg-white/[0.03] px-4 py-2.5">
          <span className="h-3 w-3 rounded-full bg-red-500/70" />
          <span className="h-3 w-3 rounded-full bg-yellow-500/70" />
          <span className="h-3 w-3 rounded-full bg-green-500/70" />
          <span className="ml-2 font-mono text-xs text-slate-500">
            train_model.py — DRAC
          </span>
          <div className="ml-auto flex items-center gap-2">
            <button
              type="button"
              onClick={() => setAutoScroll((p) => !p)}
              className={`rounded border px-2 py-0.5 text-[10px] transition-colors ${
                autoScroll
                  ? "border-emerald-500/40 text-emerald-400"
                  : "border-white/10 text-slate-500"
              }`}
            >
              {autoScroll ? "auto-scroll ✓" : "auto-scroll"}
            </button>
          </div>
        </div>

        {/* Log lines */}
        <div className="scrollbar-thin scrollbar-thumb-white/10 flex-1 overflow-y-auto p-4 font-mono text-xs leading-relaxed">
          {logs.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center gap-2 text-slate-600">
              <span className="text-4xl">⌛</span>
              <p>Waiting for training job to start…</p>
              <p className="text-[10px]">
                Logs will appear here once the daily Slurm job is submitted via
                Airflow.
              </p>
            </div>
          ) : (
            logs.map((l, i) => (
              <div
                key={i}
                className="group flex gap-3 rounded px-1 hover:bg-white/[0.02]"
              >
                <span className="w-16 shrink-0 select-none text-slate-600">
                  {l.ts}
                </span>
                <span className={`w-14 shrink-0 ${LEVEL_STYLES[l.level] ?? "text-slate-300"}`}>
                  [{l.level}]
                </span>
                {l.step && (
                  <span className="w-20 shrink-0 text-sky-500/70">{l.step}</span>
                )}
                <span className={`flex-1 break-all ${LEVEL_STYLES[l.level] ?? "text-slate-300"}`}>
                  {l.message}
                </span>
                {l.progress >= 0 && (
                  <span className="shrink-0 select-none text-slate-600">
                    {l.progress.toFixed(0)}%
                  </span>
                )}
              </div>
            ))
          )}
          <div ref={bottomRef} />
        </div>
      </div>
    </div>
  )
}

function Pill({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-xs">
      <span className="text-slate-500">{label}: </span>
      <span className="font-mono text-slate-200">{value}</span>
    </div>
  )
}

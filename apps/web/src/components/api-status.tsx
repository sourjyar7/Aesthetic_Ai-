"use client";

import { useEffect, useState } from "react";

type ReadyResponse = { status: "ready"; postgres: string; pgvector: string };

type ApiState =
  | { kind: "checking" }
  | { kind: "ready"; postgres: string; pgvector: string }
  | { kind: "unreachable"; reason: string };

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
// Generous: the first request after Neon has been idle includes its wake-up time.
const TIMEOUT_MS = 10_000;

export function ApiStatus() {
  const [state, setState] = useState<ApiState>({ kind: "checking" });

  useEffect(() => {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort("timeout"), TIMEOUT_MS);

    fetch(`${API_URL}/api/health/ready`, { signal: controller.signal })
      .then(async (response) => {
        if (!response.ok) {
          const body = (await response.json().catch(() => null)) as { reason?: string } | null;
          setState({ kind: "unreachable", reason: body?.reason ?? `HTTP ${response.status}` });
          return;
        }
        const body = (await response.json()) as ReadyResponse;
        setState({ kind: "ready", postgres: body.postgres, pgvector: body.pgvector });
      })
      .catch((error: unknown) => {
        // Ignore the abort fired by the effect cleanup (unmount / React strict-mode re-run).
        if (controller.signal.aborted && controller.signal.reason !== "timeout") return;
        const timedOut = controller.signal.reason === "timeout";
        setState({
          kind: "unreachable",
          reason: timedOut ? "timed out" : error instanceof Error ? error.message : "network error",
        });
      })
      .finally(() => clearTimeout(timeout));

    return () => {
      clearTimeout(timeout);
      controller.abort("unmounted");
    };
  }, []);

  const styles = {
    checking: "border-zinc-300 text-zinc-600 dark:border-zinc-700 dark:text-zinc-400",
    ready: "border-emerald-300 bg-emerald-50 text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-300",
    unreachable: "border-rose-300 bg-rose-50 text-rose-800 dark:border-rose-800 dark:bg-rose-950 dark:text-rose-300",
  }[state.kind];

  const dot = { checking: "bg-zinc-400 animate-pulse", ready: "bg-emerald-500", unreachable: "bg-rose-500" }[
    state.kind
  ];

  return (
    <div
      role="status"
      aria-live="polite"
      className={`inline-flex w-fit items-center gap-2 rounded-full border px-3 py-1.5 text-sm ${styles}`}
    >
      <span className={`h-2 w-2 rounded-full ${dot}`} aria-hidden />
      <span className="font-medium">API</span>
      {state.kind === "checking" && <span>checking…</span>}
      {state.kind === "ready" && (
        <span>
          ready · Postgres {state.postgres} · pgvector {state.pgvector}
        </span>
      )}
      {state.kind === "unreachable" && <span>unreachable ({state.reason})</span>}
    </div>
  );
}

# Aesthetic web

Next.js 16 (App Router, TypeScript, Tailwind CSS). Part of the Aesthetic monorepo; run commands from the repo root:

```bash
pnpm install
pnpm dev:web     # http://localhost:3000 (start the API first for the status badge)
pnpm lint
pnpm typecheck
pnpm build
```

Settings: copy `.env.example` to `.env.local` (`NEXT_PUBLIC_API_URL`, default `http://localhost:8000`).

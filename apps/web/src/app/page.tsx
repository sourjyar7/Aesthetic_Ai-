import { ApiStatus } from "@/components/api-status";

export default function Home() {
  return (
    <main className="flex flex-1 items-center justify-center px-6 py-24">
      <div className="flex w-full max-w-2xl flex-col gap-8">
        <span className="w-fit rounded-full bg-zinc-100 px-3 py-1 text-xs font-medium uppercase tracking-wider text-zinc-600 dark:bg-zinc-900 dark:text-zinc-400">
          Prototype · Phase 0
        </span>
        <div className="flex flex-col gap-4">
          <h1 className="text-5xl font-semibold tracking-tight">Aesthetic</h1>
          <p className="text-lg leading-8 text-zinc-600 dark:text-zinc-400">
            Describe the look you want in your own words. Aesthetic builds the outfit and finds
            real products that match.
          </p>
        </div>
        <ApiStatus />
      </div>
    </main>
  );
}

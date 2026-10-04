# Plan: Phase 0 — Foundation + Embedding Spike

> **Status:** Draft for review · 2026-10-04
> **Product:** Aesthetic — a fashion-first conversational stylist (flooring follows as the second vertical)
> **Repo root:** `/Users/spurge/personal/shopping_agent`
> **How to use this plan:** steps run in order. Each step is self-contained: it says what to build, which docs to copy from, how to verify it, and what not to do. A new session should read **Step 0** first, then the step it is executing.

---

## Goal

1. **Foundation** — a repo where the stack runs locally with one command each (Postgres + pgvector, FastAPI, Next.js), with lint, type checks, tests and CI wired up.
2. **Embedding spike** — measured evidence, on real fashion listings, of whether text-to-image embedding search finds texture and design details that the metadata never mentions, and which of three embedding models to carry into Phase 1.

## Out of scope

LLM integration (no API key needed yet), the multi-store collector, the chat UI, style versioning, deployment, and hosting on GitHub (the CI workflow is written, but runs only once a remote exists).

## Decisions this plan assumes

| Area | Choice | Why |
|---|---|---|
| Repo | Monorepo in the current folder, branch `main` | One place for web, API, engine, data pipeline, evaluation |
| Python | 3.12 (uv-managed), uv workspace: root package `aesthetic` (`ai/`, `catalog/`, `evaluation/`) + member `apps/api` (`aesthetic-api`) | Keeps the spec's `python -m catalog…` / `python -m evaluation…` commands; the API depends on the engine |
| PyTorch | Installed from the PyTorch CPU index on every platform | macOS builds still include Apple-GPU (MPS) support; CI never downloads multi-GB CUDA builds |
| Database | Neon (hosted Postgres 18 + pgvector 0.8.x) for development and the demo; `pgvector/pgvector:pg18-trixie` container only in CI | Filters and vector search in one SQL query; no local Docker needed; CI stays free and isolated |
| Not yet | Redis, object storage, queues, Kubernetes | No concrete need in Phase 0 |
| API | FastAPI + SQLAlchemy 2 + psycopg 3 + Alembic + pydantic-settings | Typed, standard, simple |
| Web | Next.js 16 (App Router, TypeScript, Tailwind, ESLint), pnpm workspace | Matches the spec |
| Embedding models | All loaded through `open_clip` (one API, no `trust_remote_code`): `marqo-fashion-siglip`, `siglip2-base`, `openclip-b32` | Fashion-tuned vs. newer general vs. classic CLIP baseline |
| Data | `Marqo/KAGL` on Hugging Face (Kaggle Fashion Product Images mirror, MIT-listed), ~4 of 35 shards ≈ 5k products | Real listings with labels, no login needed |

## Open questions (default in bold)

1. Licence for the repo: **MIT** / other / none for now.
2. Move the original flooring spec to `docs/specs/flooring-spec-v1.md`: **yes** / leave it at the root.
3. GitHub: **local git only for now** (you create the remote later; `gh` isn't installed) / set it up now.
4. Spike models: **all three** / drop the OpenCLIP baseline (saves ~0.6 GB).

## Downloads (≈ 5–7 GB in total; 221 GB free)

| What | From | Approx. size |
|---|---|---|
| Python 3.12 | uv-managed build | ~40 MB |
| Python packages (torch, open_clip, timm, transformers, pyarrow, FastAPI, …) | PyPI + download.pytorch.org (CPU index) | ~1–1.5 GB installed |
| `pgvector/pgvector:pg18-trixie` | Docker Hub | ~150–200 MB |
| Next.js app dependencies | npm registry | ~300–500 MB |
| Model weights × 3 | Hugging Face | ~3 GB |
| KAGL sample (4 parquet shards) | Hugging Face `Marqo/KAGL` | ~1.4–1.9 GB |

Exact dataset sizes are printed with a dry run before anything is downloaded (Step 6).

## Target layout

```text
shopping_agent/
├── apps/
│   ├── api/                  FastAPI service (uv member "aesthetic-api", package aesthetic_api/)
│   └── web/                  Next.js 16 app (pnpm)
├── ai/                       engine package — embeddings/ first
├── catalog/                  data pipeline CLIs — kagl/ (download, prepare, embed)
├── evaluation/               datasets/, spike/ runner, reports/ (generated, mostly ignored)
├── docs/
│   ├── specs/                product specs
│   ├── plans/                this plan
│   ├── decisions/            ADRs
│   ├── experiments/          experiment write-ups (+ assets/)
│   └── architecture.md
├── data/                     git-ignored: raw/, processed/, embeddings/
├── tests/                    tests for ai/, catalog/, evaluation/
├── pyproject.toml            uv workspace root + root package
├── Makefile
├── package.json, pnpm-workspace.yaml
└── .github/workflows/ci.yml
```

---

## Step 0 — Documentation discovery (completed during planning)

### Environment (verified 2026-10-04)

- Apple M1 Pro, 16 GB RAM, macOS arm64; 221 GB free disk.
- Docker 29.1.3 running (VM: 10 CPUs, ~8 GB RAM); port 5432 free.
- uv 0.12.15; Pythons present: 3.13.12 (Homebrew), 3.9.6 (system) — uv will install 3.12.
- Node 20.19.6, pnpm 10.29.3, git 2.50.1, psql 18.1 client; `gh` not installed; no Hugging Face cache yet.

### Allowed APIs

| Area | Use exactly this | Source |
|---|---|---|
| uv workspace | Root: `[tool.uv.workspace] members = ["apps/api"]`. Member dependency: `[tool.uv.sources] aesthetic = { workspace = true }`. Run in a member: `uv run --package aesthetic-api …`. The root is itself a member and needs its own `pyproject.toml`. | https://docs.astral.sh/uv/concepts/projects/workspaces/ |
| PyTorch via uv | `[[tool.uv.index]] name = "pytorch-cpu"`, `url = "https://download.pytorch.org/whl/cpu"`, `explicit = true`; `[tool.uv.sources] torch = [{ index = "pytorch-cpu" }]` (same for `torchvision`). | https://docs.astral.sh/uv/guides/integration/pytorch/ |
| FastAPI | Install `fastapi[standard]`; dev server `uv run fastapi dev <path/to/main.py>`; docs at `/docs`. | https://fastapi.tiangolo.com/tutorial/first-steps/ |
| pgvector (SQL) | `CREATE EXTENSION vector;` · column `vector(768)` · cosine distance `<=>` · `CREATE INDEX ON t USING hnsw (embedding vector_cosine_ops);` · filtered HNSW queries: `SET hnsw.iterative_scan = strict_order;` · current version 0.8.7. | https://github.com/pgvector/pgvector |
| pgvector (Python) | `pip install pgvector`; psycopg 3: `from pgvector.psycopg import register_vector`, `register_vector(conn)`; SQLAlchemy: `from pgvector.sqlalchemy import VECTOR`, `mapped_column(VECTOR(768))`, `.cosine_distance(q)`, `Index(name, col, postgresql_using="hnsw", postgresql_with={"m": 16, "ef_construction": 64}, postgresql_ops={"embedding": "vector_cosine_ops"})`. | https://github.com/pgvector/pgvector-python |
| Postgres 18 image | `PGDATA` is `/var/lib/postgresql/18/docker`; the volume is `/var/lib/postgresql`; `*.sql` in `/docker-entrypoint-initdb.d/` runs on first init; env `POSTGRES_USER` / `POSTGRES_PASSWORD` (required) / `POSTGRES_DB`. | https://github.com/docker-library/docs/blob/master/postgres/content.md |
| Next.js | `pnpm create next-app apps/web --ts --tailwind --eslint --app --src-dir --use-pnpm --import-alias "@/*" --disable-git --yes` (create-next-app 16.3.x; Turbopack and `AGENTS.md`/`CLAUDE.md` on by default). | https://nextjs.org/docs/app/api-reference/cli/create-next-app |
| CI actions | `actions/checkout@v6`; `astral-sh/setup-uv@v10` (`enable-cache`, `python-version`); `pnpm/action-setup@v6` (`cache: true`, version read from `packageManager`); `actions/setup-node@v4` (`cache: pnpm`). | setup-uv and pnpm/action-setup READMEs |
| HF download | `hf_hub_download(repo_id="Marqo/KAGL", repo_type="dataset", filename="data/data-00000-of-00035.parquet")`; `dry_run=True` lists sizes; cache in `~/.cache/huggingface/hub` (or `local_dir=`). | https://huggingface.co/docs/huggingface_hub/guides/download |
| KAGL schema | `image` (Image), `gender`, `category1`, `category2`, `category3`, `baseColour`, `season`, `year` (float64), `usage`, `text`, `item_ID` (int64); 44,434 rows; 35 shards `data/data-000NN-of-00035.parquet` (205–479 MB each). | datasets-server `/info?dataset=Marqo/KAGL`; repo tree |
| open_clip | `open_clip.create_model_and_transforms(name, pretrained=…)` → `(model, preprocess_train, preprocess_val)`; `open_clip.get_tokenizer(name)`; `model.encode_image(x, normalize=True)`; `model.encode_text(t, normalize=True)`; `hf-hub:` prefix loads from Hugging Face; `open_clip.list_pretrained()`. | open_clip README; Marqo model card |
| Marqo-FashionSigLIP | `create_model_and_transforms("hf-hub:Marqo/marqo-fashionSigLIP")`; `get_tokenizer("hf-hub:Marqo/marqo-fashionSigLIP")`; Apache-2.0; ~0.2B params; based on ViT-B-16-SigLIP. | https://huggingface.co/Marqo/marqo-fashionSigLIP |
| SigLIP 2 base | Registered in open_clip as `ViT-B-16-SigLIP2` → `timm/ViT-B-16-SigLIP2`; load with `hf-hub:timm/ViT-B-16-SigLIP2`. Trained on lowercased text padded to 64 tokens. | open_clip `pretrained.py`; transformers SigLIP2 docs (v5.17) |
| OpenCLIP baseline | `create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k")`; `get_tokenizer("ViT-B-32")`; weights at `laion/CLIP-ViT-B-32-laion2B-s34B-b79K`. | open_clip README, `docs/PRETRAINED.md` |

### Anti-patterns — do not do these

- Don't load Marqo-FashionSigLIP through `transformers` with `trust_remote_code=True`: transformers is now v5 and the custom code targets v4. Use open_clip.
- Don't copy `torch.cuda.amp.autocast()` / `torch.autocast("cuda")` from model cards. There is no CUDA on the M1; run fp32 on `mps`, falling back to `cpu`.
- Don't tokenize SigLIP text by hand. Use the open_clip tokenizer for the same model id (it pads to 64 tokens) and lowercase the text.
- Don't compare vectors from different models, or text and image vectors from different models.
- Don't mount the Postgres 18 volume at `/var/lib/postgresql/data`; mount it at `/var/lib/postgresql`.
- Don't expect HNSW results to equal numpy results — HNSW is approximate. Parity is checked with exact search; HNSW is measured as recall@10.
- Don't install CUDA builds of torch in CI; use the CPU index.
- Don't hard-code model ids outside `ai/embeddings/registry.py`.
- Don't type numbers into the experiment report by hand; generate them from `results.json`.
- Don't commit `data/`, model weights or `.env`.

### Known gaps (resolved during execution)

- Which extras open_clip needs for the SigLIP models (`timm`, `transformers`, maybe `sentencepiece`) → install `timm` + `transformers`; confirm by loading each model in Step 7.
- Embedding size per model → read from model output in Step 7 (expected 768 for the SigLIP family, 512 for ViT-B-32).
- Whether KAGL shards are grouped by category → check shard 0 in Step 6 before downloading more.
- Exact parquet type of the `image` column (likely a struct of bytes + path) → inspect the schema in Step 6.
- Next.js 16's minimum Node version → check `engines` after install (we have 20.19.6).

---

## Step 1 — Repo skeleton and Python tooling ✅ (done 2026-10-04)

**Implement**
1. `git init -b main`; `.gitignore` (Python, Node, `.env`, `.venv`, `data/`, `.next`, `node_modules`, `evaluation/reports/`), `.editorconfig`, stub `README.md`, `LICENSE` (open question 1).
2. Move the flooring spec into `docs/specs/` (open question 2); this plan stays in `docs/plans/`.
3. `uv python pin 3.12` → `.python-version`.
4. Root `pyproject.toml`: project `aesthetic` built with hatchling (`[tool.hatch.build.targets.wheel] packages = ["ai", "catalog", "evaluation"]`); workspace `members = ["apps/api"]`; the PyTorch CPU index + sources from Step 0; dependency group `dev` = ruff, mypy, pytest. Tool config: ruff (line length 100; rules E, F, I, UP, B), mypy (strict for `ai/`), pytest (markers `integration` and `slow`; test paths).
5. Empty packages (`__init__.py`) and `tests/test_smoke.py`.

**Docs:** uv workspaces; uv PyTorch guide.
**Verify:** `uv sync` ✓ · `uv run ruff check .` ✓ · `uv run mypy ai catalog evaluation` ✓ · `uv run pytest` ✓ · first commit.
**Guards:** the root must be a workspace member with its own `pyproject.toml`; no torch from PyPI CUDA wheels.

## Step 2 — Postgres + pgvector on Neon ✅ (done 2026-10-04)

*Changed from the original draft: hosted Neon instead of a local Docker container.*

**Implemented**
1. Neon project (Free plan), Postgres 18.6, region `ap-southeast-1` (Singapore), database `neondb`.
2. `CREATE EXTENSION IF NOT EXISTS vector;` run in the Neon SQL editor (Step 3's migration repeats it so any new database gets it).
3. `.env.example` (committed template) and `.env` (git-ignored, mode 600) with the **direct** (unpooled) `DATABASE_URL` using the `postgresql+psycopg://` prefix.

**Docs:** https://neon.com/docs/extensions/pgvector — pgvector on every plan; `CREATE EXTENSION IF NOT EXISTS vector;`; `vector` up to 2,000 dimensions. Free plan: 1 GB storage per project, 100 CU-hours/month, scales to zero after 5 minutes idle.
**Verified:** `psql` → `server_version` 18.6, `pgvector` 0.8.6, `'[1,0,0]'::vector <=> '[0,1,0]'::vector` = 1.
**Guards:** use the direct URL for migrations (the pooled `-pooler` host is for the deployed API later); never print or commit the connection string; latency measured against Neon includes network time — report database time from `EXPLAIN ANALYZE` separately; the first query after an idle pause is slower (cold start).

## Step 3 — FastAPI service skeleton ✅ (done 2026-10-04)

**Implement** (`apps/api`, package `aesthetic_api`)
1. `apps/api/pyproject.toml`: `aesthetic-api`; deps `fastapi[standard]`, `pydantic-settings`, `sqlalchemy>=2`, `psycopg[binary]`, `pgvector`, `alembic`, `aesthetic` (workspace source).
2. `settings.py` (BaseSettings: `database_url`, `cors_origins`, `log_level`; reads `.env`), `db.py` (engine + session factory), `main.py` (`app = FastAPI(...)`, CORS for `http://localhost:3000`, request-ID middleware that accepts or creates `X-Request-ID`, returns it, and logs method/path/status/latency as JSON), `routes/health.py`:
   - `GET /api/health` → `{"status": "ok"}` (no database).
   - `GET /api/health/ready` → `select 1` + pgvector version → `200 {"status": "ready", "postgres": …, "pgvector": …}` or `503`.
3. Alembic in `apps/api/alembic/` (`env.py` reads `settings.database_url`); migration `0001_enable_pgvector`: `op.execute("CREATE EXTENSION IF NOT EXISTS vector")`.
4. Tests in `apps/api/tests/`: health returns ok and echoes `X-Request-ID`; readiness test marked `integration` (needs the database).

**Docs:** FastAPI first steps; pgvector-python; Alembic tutorial (`alembic init`, `op.execute`).
**Verify:** `uv run --package aesthetic-api fastapi dev apps/api/aesthetic_api/main.py` → `curl -i localhost:8000/api/health/ready` returns 200 with versions and `X-Request-ID` · `uv run alembic -c apps/api/alembic.ini upgrade head` ✓ · tests ✓.
**Guards:** settings only from the environment; no tables yet beyond the extension.

## Step 4 — Next.js web shell ✅ (done 2026-10-04)

**Implement**
1. Root `package.json` (`"private": true`, `"packageManager": "pnpm@10.29.3"`, scripts `dev:web`, `lint`, `typecheck`, `build`) and `pnpm-workspace.yaml` (`packages: ["apps/web"]`).
2. `pnpm create next-app apps/web --ts --tailwind --eslint --app --src-dir --use-pnpm --import-alias "@/*" --disable-git --yes`.
3. Read the generated `apps/web/AGENTS.md` before writing code. Replace the starter page with a minimal placeholder: product name, one-line promise, and an **API status** badge (client component) that fetches `${NEXT_PUBLIC_API_URL}/api/health/ready` and shows *ready* or *unreachable*. Add `apps/web/.env.example` with `NEXT_PUBLIC_API_URL=http://localhost:8000`.

**Docs:** create-next-app reference; generated `AGENTS.md`.
**Verify:** `pnpm --filter web dev` → localhost:3000 renders; the badge says *ready* with API + DB up and *unreachable* with the API down · `pnpm --filter web lint` ✓ · `pnpm --filter web exec tsc --noEmit` ✓ · `pnpm --filter web build` ✓.
**Guards:** App Router only (no Pages Router APIs such as `getServerSideProps`); nothing secret in `NEXT_PUBLIC_*`; no design work yet.

## Step 5 — Dev commands, CI and docs

**Implement**
1. `Makefile`: `setup` (uv sync + pnpm install), `migrate`, `api`, `web`, `lint`, `typecheck`, `test`, `spike` (runs Steps 6–12 end to end from cached data).
2. `.github/workflows/ci.yml`:
   - **python** — checkout → setup-uv (cache, Python 3.12) → `uv sync --all-packages --locked` → ruff → mypy → migrations → `pytest -m "not slow"` with a `pgvector/pgvector:pg18-trixie` service container and `DATABASE_URL` set.
   - **web** — checkout → pnpm/action-setup (cache) → setup-node (Node 20, pnpm cache) → `pnpm install --frozen-lockfile` → lint → typecheck → build.
3. Docs: `README.md` (what it is, quickstart, repo map, status); `docs/architecture.md` (current and planned components, with a diagram); ADRs in `docs/decisions/`: 0001 fashion-first, 0002 pre-built listing index instead of live web search, 0003 Postgres + pgvector, 0004 embedding candidates via open_clip, 0005 uv + pnpm monorepo.

**Verify:** `make lint typecheck test` ✓ locally; CI runs on the first push (open question 3).
**Guards:** no Redis/queues/object storage; CI must not pull CUDA torch.

## Step 6 — Spike data: download and prepare a KAGL sample

**Implement** (`catalog/kagl/`)
1. Add data deps to the root package: `huggingface_hub`, `pyarrow`, `pillow`, `numpy`, `tqdm`, `pyyaml`.
2. `python -m catalog.kagl.download --shards 0 --dry-run` prints sizes; then download shard 0 only.
3. Inspect shard 0: `pyarrow.parquet.read_schema` (confirm the `image` column type), row count, `category1` / `category3` histograms. If shard 0 is mixed → download shards 1–3. If rows are grouped by category → pick four shards spread across the range (e.g. 0, 11, 22, 33). Record the choice in the experiment log.
4. `python -m catalog.kagl.prepare`: stream row batches; keep `category1 ∈ {Apparel, Footwear, Accessories}`; decode each image → RGB → `data/processed/kagl/images/{item_ID}.jpg` (longest side 512, quality 90); write `data/processed/kagl/products.parquet` (all metadata + `image_path`, sorted by `item_ID`); save category/colour histograms to `data/processed/kagl/stats.json`.
5. Unit test on a 3-row synthetic parquet fixture (generated image bytes) covering filtering, decoding and the output schema.

**Docs:** HF download guide; KAGL schema (Step 0).
**Verify:** ~4–5k products; every `image_path` opens; stats look sane; re-running is a no-op.
**Guards:** never load all shards into memory at once; don't commit data; `item_ID` is the product key.

## Step 7 — Embedder interface and the three model adapters

**Implement** (`ai/embeddings/`)
1. Deps: `torch`, `torchvision` (CPU index), `open_clip_torch`, `timm`, `transformers`.
2. `base.py`: `Embedder` protocol — `model_key`, `dim`, `encode_images(images) -> np.ndarray` (N×dim, float32, L2-normalised), `encode_texts(texts) -> np.ndarray`.
3. `registry.py`: the three models (key → open_clip name / pretrained tag, licence, notes). Model ids live only here.
4. `open_clip_embedder.py`: one adapter for all three — `create_model_and_transforms` (use `preprocess_val`), `get_tokenizer` for the same id, device `mps` if `torch.backends.mps.is_available()` else `cpu`, `model.eval()`, `torch.inference_mode()`, fp32, batching, `encode_image` / `encode_text` with `normalize=True`, texts lowercased.
5. `python -m ai.embeddings.smoke`: per model, print device, dim, tokenizer output shape and time per batch of 32 images.
6. Tests: a fake embedder for unit tests of downstream code; one `slow` test per model checking shapes, unit norms, and that a solid red image scores closer to "a red image" than to "a blue image".

**Docs:** open_clip README; Marqo model card; open_clip pretrained registry; transformers SigLIP2 tips.
**Verify:** smoke runs for all three on MPS · `open_clip.list_pretrained()` contains `("ViT-B-32", "laion2b_s34b_b79k")` (otherwise use `hf-hub:laion/CLIP-ViT-B-32-laion2B-s34B-b79K`) · SigLIP tokenizers return `[N, 64]`.
**Guards:** Step 0 anti-patterns (no CUDA autocast, no `trust_remote_code`, ids only in the registry).

## Step 8 — Embed the sample with each model

**Implement** `python -m catalog.kagl.embed --model <key> | --all`
- Batches over `products.parquet`; chunked writes to `data/embeddings/<model_key>/`: `image_vectors.npy`, `text_vectors.npy` (listing `text`), `ids.npy`, `meta.json` (model key and source, dim, count, device, seconds, images/sec, date, git SHA).
- Resumable: skips complete outputs and restarts from the last finished chunk.

**Verify:** counts equal the product count for every model; norms within 1 ± 1e-3; throughput recorded in `meta.json`.
**Guards:** one directory per model + version; never overwrite another model's vectors.

## Step 9 — Query set and spike runner

**Implement**
1. `evaluation/datasets/spike_queries.yaml` — ~25 queries, final wording adjusted to what the sample actually contains (check `stats.json` first). Each query has `id`, `text`, `group`, optional `filters` (`gender`, `category3`), and for group A the `expect` labels.
   - **A. Metadata-checkable** (~8, auto-scored, no filters): e.g. "navy blue formal shirt for men", "red kurta for women", "black heels", "white sports shoes", "brown leather belt", "pink saree".
   - **B. Texture / design not in metadata** (~10, judged, with a category filter): e.g. "distressed light-wash jeans", "floral print kurta", "checked casual shirt", "striped t-shirt", "graphic print t-shirt", "polka dot dress", "embroidered kurta", "colour-block sports shoes", "metallic gold heels", "analog watch with a brown leather strap".
   - **C. Niche terms** (~3, judged): "chikankari kurta", "bandhani print", "mirror work kurta" — each paired with a plain visual rewrite (what the LLM would write) to measure the gain.
   - **D. Style / vibe** (~3, judged): "minimal office wear for women", "festive ethnic wear for men", "sporty summer look".
   - **E. Negation probe** (1–2): "kurta without embroidery" — expected to fail; documents why dislikes become filters/penalties.
   - **F. Image → image** (3 seed products): nearest neighbours ("more like this").
2. `python -m evaluation.spike.run`: for each model × query — encode the lowercased text, exact cosine search over image vectors in numpy, apply filters, take the top 10. Score variants: `image` (primary), `text` (listing text), `fused` (0.7 image + 0.3 text, z-normalised per query; exploratory). Write `evaluation/reports/spike-001/results.json` (top-10 ids and scores per model/query/variant, plus timings).
3. Auto-score group A: P@10 with all expected labels matching, and category-only P@10.

**Docs:** original spec §28–§32 (metrics and methodology).
**Verify:** `results.json` covers every model × query × variant; group A scores computed; text-encoding latency per query recorded (MPS and CPU).

## Step 10 — Visual report and blind judging

**Implement** `python -m evaluation.spike.report`
1. One contact-sheet PNG per query: a row per model, top-10 thumbnails (128 px) with rank and score. Rows are labelled **Model A / B / C**; the mapping is stored separately in `key.json` so judging is blind.
2. Static `evaluation/reports/spike-001/index.html` linking all grids, group A scores and timings.
3. Judging groups B–E: Claude reviews each blind grid and records a hit/miss per rank in `evaluation/spike/judgments.yaml` (query, model letter, rank, hit, note); you spot-check a subset and overrule where you disagree. Then reveal the key and compute hits@10 and first-hit rank per model.
4. Optional: for filtered categories under 100 items, label the whole category once to get true recall.

**Verify:** every judged query has labels for all three models; scores come from `judgments.yaml`, never typed by hand.

## Step 11 — pgvector parity check

**Implement** `python -m evaluation.spike.pgvector_check`
1. On Neon, per model, a table `spike_<model_key>` (`item_id bigint primary key`, `gender`, `category3`, `base_colour`, `embedding vector(<dim>)`), bulk-inserted with psycopg 3 + `register_vector`.
2. Exact search (no index): `ORDER BY embedding <=> %s LIMIT 10`, plus `WHERE category3 = %s` for filtered queries → compare with the numpy top 10 for every query (ignoring order among exact ties).
3. Build an HNSW index (`vector_cosine_ops`) → recall@10 against exact search; p50/p95 latency both end-to-end and database-only (`EXPLAIN ANALYZE`); filtered queries with `SET hnsw.iterative_scan = strict_order;` must still return 10 rows.

**Verify:** exact parity on every query; HNSW recall@10 reported (expect ≥ 0.95); latency added to `results.json`.
**Guards:** don't expect HNSW to equal exact search; spike tables are not part of the migrations and are dropped afterwards.

## Step 12 — Experiment write-up and model decision

**Implement**
1. `docs/experiments/001-embedding-model-spike.md`, following the spec's §32 template:
   - Hypotheses — H1: embeddings find texture/design absent from metadata; H2: the fashion-tuned model beats the general ones; H3: negation fails; H4: plain visual rewrites help niche terms.
   - Setup (sample, models and revisions, hardware, query set), controlled variables.
   - Results tables generated from `results.json` and `judgments.yaml`; 4–6 representative grids (committed).
   - Analysis, limitations (small sample, one primary judge, a single dated store, 224 px input), decision.
2. ADR `docs/decisions/0006-embedding-model.md` recording the chosen model and why.

**Decision rule:** carry forward the model with the best combined score on groups A + B. Flag any group where the winner averages under 5/10 as a Phase 1 risk, with a mitigation (LLM rewrite, image crops, a higher-resolution model).
**Verify:** every number in the write-up traces to `results.json` / `judgments.yaml` (a script prints the tables the doc embeds).

## Step 13 — Final verification

- Fresh clone + `.env` → `make setup && make migrate && make test` ✓; `make api` + `make web` → the badge shows *ready*.
- `make spike` reproduces `results.json` from cached data and vectors (same top-10s).
- Anti-pattern greps: no `cuda` in `ai/ catalog/ evaluation/`; no `trust_remote_code`; model ids only in `ai/embeddings/registry.py`; `git grep -nE "(PASSWORD|API_KEY)=" -- ':!*.example'` finds nothing; `.env` and `data/` are ignored.
- Lint, type checks and tests green; one commit per step with a clear message.

---

## Execution order

Steps 1 → 5 build the foundation. Start Step 6's shard-0 download right after Step 1 so it runs in the background. Then 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13.

## Definition of done

- The stack runs locally; health and readiness verified; CI workflow in place.
- ~5k real products embedded with three models; ~25 queries scored; blind-judged grids; pgvector parity proven.
- An experiment write-up with real, reproducible numbers and a model decision; ADRs 0001–0006 written.

# Aesthetic

A conversational, multimodal shopping assistant. Describe the look you want in your own words, and Aesthetic builds the outfit and finds real products that match. Fashion comes first; flooring follows as a second vertical.

> **Status:** prototype, Phase 0 in progress (foundation + embedding-model spike).
> Plan: [docs/plans/phase-0-foundation-and-embedding-spike.md](docs/plans/phase-0-foundation-and-embedding-spike.md)

## Repository layout

| Path | Contents |
|---|---|
| `ai/` | Engine: embeddings, retrieval, ranking |
| `catalog/` | Data pipeline: download, prepare and embed product listings |
| `evaluation/` | Benchmarks, experiment runners and reports |
| `docs/` | Specs, plans, decisions and experiment write-ups |
| `tests/` | Tests for the Python packages |

## Development

Requires [uv](https://docs.astral.sh/uv/). uv installs the pinned Python (3.12) and manages the virtual environment.

```bash
uv sync                 # install dependencies into .venv
uv run ruff check .     # lint
uv run mypy ai catalog evaluation tests
uv run pytest
```

## Licence

MIT. See [LICENSE](LICENSE).

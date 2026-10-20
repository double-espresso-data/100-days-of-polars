# 100 Days of Polars

Learning Polars and publishing a 100-post series on Medium.

| Folder | What lives there |
| --- | --- |
| `00_plan/` | `roadmap.md` (all 100 topics), `tracker.csv` (status per day), `post_template.md` |
| `learning/` | scratch notebooks while learning (not committed) |
| `notebooks/` | published notebook per day, linked from the post: `day_001_why_polars.ipynb` |
| `posts/` | Medium posts in markdown: `day_001_why_polars.md` |
| `data/raw`, `data/processed` | datasets (not committed): e-commerce orders for Days 1–54, NYC taxi from Day 55 |
| `assets/` | images and diagrams for posts |

Setup: `uv sync` (creates `.venv` from `pyproject.toml` and `uv.lock`). Run notebooks with the `.venv` kernel; they start in the project root, so use paths like `data/raw/...`.

# 100 Days of Polars — Roadmap

Source of truth: https://claude.ai/code/artifact/d49c336a-daaf-418f-bd65-ef02c74b385f (local copy exported Oct 19, 2026)

## Series overview

100 posts over about 29 weeks (3–4 a week), taking an intermediate data engineer to expert-level Polars. The series skips "what is a dataframe" and goes straight to how Polars thinks: expressions, lazy plans, Arrow memory and the query optimizer.

- **Reader:** data engineers and analysts who already know pandas, Spark or SQL.
- **Length:** 5–8 minute read, one idea per post, every post with runnable code.
- **Arc:** foundations → expressions → types → aggregation → joins → lazy engine → IO at scale → performance → production → migration and extending.
- **Post template:** the problem (a real data engineering pain), the Polars way, a pandas/SQL comparison where it helps, one gotcha, a 3-line takeaway, and a teaser for tomorrow.
- **Running dataset:** two, switched at the lazy phase. Days 1–54 use a multi-table e-commerce orders set (orders, order items, customers, products, payments; for example the public Olist dataset), so joins and star schemas feel real. Days 55–100 switch to NYC taxi trips (tens of millions of rows in Parquet) to show what lazy execution, pushdowns and streaming do at scale.

## Phase map

| Phase | Name | Days |
| --- | --- | --- |
| 1 | Foundations | 1–8 |
| 2 | Expressions | 9–22 |
| 3 | Data types | 23–32 |
| 4 | Aggregation and windows | 33–44 |
| 5 | Joins and combining | 45–54 |
| 6 | Lazy engine and optimizer | 55–66 |
| 7 | IO at scale | 67–76 |
| 8 | Performance and internals | 77–86 |
| 9 | Production pipelines | 87–94 |
| 10 | Migration and extending | 95–100 |

Phases 1–5 build fluency with the API; phases 6–10 move to the engine, scale and production work.

## Day-by-day topics

### Phase 1 — Foundations and mental model (Days 1–8)

| Day | Topic | Key APIs |
| --- | --- | --- |
| 1 | Why Polars exists: where pandas hurts at scale | — |
| 2 | Arrow columnar memory and why Polars is fast | Arrow, chunks |
| 3 | Installing Polars and picking the right build | `polars`, `polars[gpu]`, `show_versions` |
| 4 | Series and DataFrame: schema, no index | `pl.Series`, `pl.DataFrame`, `schema` |
| 5 | Reading data: read vs scan | `read_csv`, `scan_csv`, `read_parquet` |
| 6 | The four contexts | `select`, `with_columns`, `filter`, `group_by` |
| 7 | Eager vs lazy in one picture | `lazy()`, `collect()` |
| 8 | pandas habits to unlearn: a cheat sheet | — |

### Phase 2 — Expressions (Days 9–22)

| Day | Topic | Key APIs |
| --- | --- | --- |
| 9 | What an expression really is | `pl.col`, `pl.lit` |
| 10 | Selecting columns by name, regex and dtype | `pl.col("^x_.*$")`, `pl.col(pl.Int64)` |
| 11 | Column selectors | `polars.selectors` |
| 12 | Arithmetic, comparison and boolean logic | `&`, `\|`, `is_between` |
| 13 | Conditional logic | `when/then/otherwise` |
| 14 | Expression expansion: one expression, many columns | `pl.all()`, `exclude` |
| 15 | Naming outputs | `alias`, `name.suffix`, `name.map` |
| 16 | Casting, strict vs non-strict | `cast`, `strict=` |
| 17 | Nulls: fill, drop, detect | `fill_null`, `drop_nulls`, `is_null` |
| 18 | Filtering inside aggregations | `filter` in `agg`, `sum_horizontal` |
| 19 | Sorting and top-k | `sort`, `sort_by`, `top_k` |
| 20 | Uniques and duplicates | `unique`, `is_duplicated`, `value_counts` |
| 21 | Reusable expression functions | `pipe`, functions returning `pl.Expr` |
| 22 | Why `map_elements` is the last resort | `map_elements`, `map_batches` |

### Phase 3 — Data types in depth (Days 23–32)

| Day | Topic | Key APIs |
| --- | --- | --- |
| 23 | The type system at a glance | `Schema`, dtypes |
| 24 | String cleaning | `str.strip_chars`, `str.replace`, `str.to_lowercase` |
| 25 | Regex extraction and parsing | `str.extract`, `str.split`, `str.contains` |
| 26 | Dates, datetimes and time zones | `str.to_datetime`, `dt.convert_time_zone` |
| 27 | Durations and date arithmetic | `dt.offset_by`, `pl.duration`, `dt.truncate` |
| 28 | Categorical vs Enum | `pl.Categorical`, `pl.Enum` |
| 29 | List columns | `list.*`, `list.eval` |
| 30 | Struct columns | `struct.field`, `unnest` |
| 31 | Array and Decimal (money done right) | `pl.Array`, `pl.Decimal` |
| 32 | Null vs NaN and other type gotchas | `is_nan`, `fill_nan` |

### Phase 4 — Aggregation, windows and reshaping (Days 33–44)

| Day | Topic | Key APIs |
| --- | --- | --- |
| 33 | group_by fundamentals | `group_by`, `agg` |
| 34 | Rich expressions inside agg | `agg` with conditions, `first`, `last` |
| 35 | Group order and determinism | `maintain_order` |
| 36 | Window functions | `over` |
| 37 | Window mapping strategies | `over(mapping_strategy=)` |
| 38 | Running totals, lags and diffs | `cum_sum`, `shift`, `diff` |
| 39 | Rolling statistics | `rolling_mean`, `rolling_*_by` |
| 40 | Time-bucketed aggregation | `group_by_dynamic` |
| 41 | Rolling windows over time | `rolling` |
| 42 | Pivot | `pivot` |
| 43 | Unpivot and transpose | `unpivot`, `transpose` |
| 44 | Exploding and imploding nested data | `explode`, `implode` |

### Phase 5 — Joins and combining (Days 45–54)

| Day | Topic | Key APIs |
| --- | --- | --- |
| 45 | Join fundamentals | `join(how="inner"\|"left"\|"full")` |
| 46 | Semi and anti joins for filtering | `how="semi"`, `how="anti"` |
| 47 | Keys, suffixes, coalesce and validate | `coalesce=`, `validate=` |
| 48 | Cross joins and when they help | `how="cross"` |
| 49 | Point-in-time joins | `join_asof` |
| 50 | Range and inequality joins | `join_where` |
| 51 | Concatenation: vertical, horizontal, diagonal | `pl.concat(how=)` |
| 52 | Join performance on lazy frames | lazy joins, `explain` |
| 53 | Upserts | `update` |
| 54 | Mini-project: build a star-schema fact table | all of the above |

### Phase 6 — The lazy engine and optimizer (Days 55–66)

| Day | Topic | Key APIs |
| --- | --- | --- |
| 55 | Switching to big data: NYC taxi trips and your first LazyFrame | `LazyFrame`, `scan_*` |
| 56 | Reading query plans | `explain`, `show_graph` |
| 57 | Predicate pushdown | `filter` + `explain` |
| 58 | Projection pushdown | `select` + `explain` |
| 59 | Slice pushdown, common subplan elimination and friends | `head`, CSE |
| 60 | Collecting many queries at once | `collect_all`, `collect_async` |
| 61 | Schema resolution and lazy pitfalls | `collect_schema` |
| 62 | The streaming engine: larger-than-memory data | `collect(engine="streaming")` |
| 63 | Profiling a query | `profile` |
| 64 | Caching and reusing lazy frames | `cache` |
| 65 | Lazy vs eager: a decision guide | — |
| 66 | SQL on Polars | `pl.sql`, `SQLContext` |

### Phase 7 — IO at scale (Days 67–76)

| Day | Topic | Key APIs |
| --- | --- | --- |
| 67 | Parquet deep dive: row groups, statistics, compression | `write_parquet` options |
| 68 | Scanning hive-partitioned data | `scan_parquet(hive_partitioning=)` |
| 69 | Writing partitioned datasets | partitioned `sink_parquet` / `write_parquet` |
| 70 | Streaming writes | `sink_parquet`, `sink_csv`, `sink_ndjson` |
| 71 | Cloud storage: S3, GCS, Azure | `storage_options`, credential providers |
| 72 | CSV and NDJSON at scale | `schema_overrides`, `infer_schema_length` |
| 73 | Delta Lake | `scan_delta`, `write_delta` |
| 74 | Apache Iceberg | `scan_iceberg` |
| 75 | Databases | `read_database`, `read_database_uri`, `write_database` |
| 76 | Interop: Arrow, DuckDB, pandas, NumPy, Excel | `to_arrow`, `from_pandas`, `read_excel` |

### Phase 8 — Performance and internals (Days 77–86)

| Day | Topic | Key APIs |
| --- | --- | --- |
| 77 | How Polars parallelises | thread pool, `POLARS_MAX_THREADS` |
| 78 | Memory: chunks and rechunking | `rechunk`, `estimated_size` |
| 79 | Sorted flags and fast paths | `set_sorted` |
| 80 | Choosing dtypes to cut memory | `shrink_dtype`, downcasting |
| 81 | Staying out of Python: vectorise everything | expressions vs UDFs |
| 82 | Fast strings and categoricals | `Categorical`, string tricks |
| 83 | Benchmarking properly | methodology, warm-up, timing |
| 84 | Benchmark: Polars vs pandas vs DuckDB vs Spark | NYC taxi trips |
| 85 | The GPU engine: when it helps | `collect(engine="gpu")` |
| 86 | Config and debugging | `pl.Config`, `show_versions` |

### Phase 9 — Production data engineering (Days 87–94)

| Day | Topic | Key APIs |
| --- | --- | --- |
| 87 | Structuring a Polars pipeline project | modules, `pipe` |
| 88 | Testing transformations | `polars.testing`, pytest |
| 89 | Schema validation | Pandera, Patito or dataframely |
| 90 | Data-quality checks as expressions | expressions, `filter` |
| 91 | Incremental loads and SCD Type 2 | `join`, `update`, `join_where` |
| 92 | Orchestration with Airflow or Dagster | — |
| 93 | Error handling, logging and version pinning | — |
| 94 | Running Polars in the cloud and distributed options | containers, Polars Cloud |

### Phase 10 — Migration and extending Polars (Days 95–100)

| Day | Topic | Key APIs |
| --- | --- | --- |
| 95 | pandas → Polars migration playbook | side-by-side recipes |
| 96 | PySpark → Polars: when one machine wins | — |
| 97 | Custom namespaces | `register_expr_namespace` |
| 98 | Expression plugins in Rust | `pyo3-polars` |
| 99 | Capstone: an end-to-end pipeline | everything |
| 100 | Retrospective and what's next | — |

## How we'll work

Learn a phase first, then write its posts, so each article comes from code you have actually run.

1. **Learn:** Claude explains the day's concepts and gives tasks; you experiment in `learning/day_NNN.ipynb` (scratch, not committed). Claude reviews it.
2. **Publish:** your code plus the review becomes `notebooks/day_NNN_<slug>.ipynb` (clean, runs top to bottom, committed), and the post becomes `posts/day_NNN_<slug>.md` from the template.
3. **Track:** `tracker.csv` holds day, topic, learn status, draft status and publish date.

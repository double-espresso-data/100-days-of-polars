# Query plans and relational algebra — learning notes

*Learned while writing Day 7 (eager vs lazy). Polars' query plans borrow their vocabulary from database theory.*

---

## 1. Projection, predicate, pushdown

| Term | Chooses | SQL | In a Polars plan |
|---|---|---|---|
| **Projection** | columns | `SELECT a, b` | `PROJECT 4/8 COLUMNS`, `simple π` |
| **Predicate** | rows | `WHERE status = 'delivered'` | `FILTER` (as written), `SELECTION:` (pushed into a scan) |

**Pushdown** moves projections and predicates as close to the data source as possible, ideally into the file reader, so data you do not need is never read at all.

---

## 2. Relational algebra symbols

Relational algebra is the maths behind SQL and query engines (E. F. Codd, 1970). Each operator takes one or two tables and returns a table, which is why operators chain together like a Polars query.

| Symbol | Name | What it does | SQL | Polars |
|---|---|---|---|---|
| **π** (pi) | Projection | keep some columns | `SELECT a, b` | `select("a", "b")` |
| **σ** (sigma) | Selection | keep rows matching a condition | `WHERE ...` | `filter(...)` |
| **ρ** (rho) | Rename | rename a table or columns | `AS` | `rename`, `alias` |
| **⋈** (bowtie) | Join (natural / inner) | combine rows with matching keys | `INNER JOIN` | `join(how="inner")` |
| **⟕** | Left outer join | all left rows, matching right rows | `LEFT JOIN` | `join(how="left")` |
| **⟖** | Right outer join | all right rows, matching left rows | `RIGHT JOIN` | `join(how="right")` |
| **⟗** | Full outer join | all rows from both sides | `FULL OUTER JOIN` | `join(how="full")` |
| **⋉** | Semi join | left rows that have a match (no right columns) | `WHERE EXISTS (...)` | `join(how="semi")` |
| **▷** | Anti join | left rows with no match | `WHERE NOT EXISTS (...)` | `join(how="anti")` |
| **×** | Cartesian product | every left row with every right row | `CROSS JOIN` | `join(how="cross")` |
| **∪** | Union | rows in either table | `UNION` | `pl.concat` + `unique()` |
| **∩** | Intersection | rows in both tables | `INTERSECT` | semi join on all columns |
| **−** | Difference | rows in the first but not the second | `EXCEPT` | anti join on all columns |
| **γ** (gamma) | Grouping / aggregation | one row per group with aggregates | `GROUP BY` | `group_by().agg()` |
| **τ** (tau) | Sort | order rows | `ORDER BY` | `sort` |

Notes:

- The confusing one: in relational algebra, **selection (σ) means filtering rows**, not choosing columns. Choosing columns is **projection (π)**. SQL's `SELECT` keyword is actually a projection.
- `γ` and `τ` are extensions used in many textbooks; the core of Codd's algebra is π, σ, ρ, ×, ∪ and −. Notation varies a little between books.
- In Polars' text plans (`explain()`) you mainly see **π**, in `simple π`. Other symbols are more common in database textbooks and some graphical plan views.

**Example.** "Names of customers in SP":

```
π name ( σ state = 'SP' ( customers ) )
```

Read inside out: start with `customers`, keep rows where the state is SP (σ), then keep only the `name` column (π). The Polars version reads in the same order, top to bottom:

```python
customers.filter(pl.col("state") == "SP").select("name")
```

---

## 3. How to read a Polars query plan

```python
print(lf.explain())                 # optimized plan (the default)
print(lf.explain(optimized=False))  # the plan as written
```

**Rules:**

1. **Read from the bottom up.** The bottom lines are the data sources (scans). Each step takes the output of the step indented below it. The top line is the last thing that happens.
2. **Indentation means "feeds into".** A line indented under another is its input. A join has two inputs: `LEFT PLAN` and `RIGHT PLAN`, ending with `END INNER JOIN`.
3. **Compare the two plans.** What moved, what disappeared and what got smaller is the optimizer's work.

**Common node names:**

| Node | Meaning |
|---|---|
| `Csv SCAN [file]` / `Parquet SCAN [file]` | read a file |
| `PROJECT 4/8 COLUMNS` | read 4 of the file's 8 columns. `*/8` means all of them |
| `SELECTION: <condition>` | a filter pushed into the scan: rows dropped while reading |
| `ESTIMATED ROWS: n` | the optimizer's guess at the size (from file size), not a count |
| `FILTER <condition> FROM` | a filter applied to the input below it (not pushed down) |
| `simple π n/n [cols]` | a projection step: keep these columns |
| `WITH_COLUMNS: [...]` | add or replace columns |
| `INNER JOIN` / `LEFT PLAN ON` / `RIGHT PLAN ON` | a join, its two inputs and their keys |
| `AGGREGATE [...] BY [keys] FROM` | `group_by(keys).agg([...])` |
| `SORT BY [...]` | `sort` |

**Day 7 example, optimized, bottom up:**

1. Scan the orders CSV, reading 4 of 8 columns and dropping non-delivered rows while reading.
2. Keep 3 columns (`order_status` has done its job).
3. Scan the customers CSV, reading 2 of 5 columns.
4. Inner join on `customer_id`.
5. Add `is_late`.
6. Keep only `customer_state` and `is_late`.
7. Aggregate by `customer_state`.
8. Sort by `late_pct`.

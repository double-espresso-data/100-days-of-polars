# collect_all and shared work — learning notes

*Learned while writing Day 7. Covered properly later in the series (collecting many queries at once; common subplan elimination; caching).*

---

## 1. The question

A LazyFrame is a plan, and every `collect()` runs its plan from scratch. So if two queries start from the same data, collecting them one by one does the shared part twice.

`pl.collect_all([q1, q2])` runs several plans in one go. Does Polars just run them side by side, or does it also share the work they have in common?

**Answer, checked on Polars 2.0.0: both.** Independent queries run in parallel. Identical parts run once and are shared.

---

## 2. The experiment

```python
base = pl.scan_csv(ORDERS).filter(pl.col("order_status") == "delivered")

by_customer = base.group_by("customer_id").agg(pl.len())
by_month    = base.group_by(pl.col("order_purchase_timestamp").dt.truncate("1mo")).agg(pl.len())

print(pl.explain_all([by_customer, by_month]))   # the combined plan collect_all would run
```

Output:

```
SINK_MULTIPLE
  PLAN 0:
    AGGREGATE[maintain_order: false]
      [len()] BY [col("customer_id")]
      FROM
      simple π 1/1 ["customer_id"]
        CACHE[id: 94a1f8f2-2a94-42d2-bd92-7a93792805db]
          simple π 2/2 ["customer_id", ... 1 other column]
            Csv SCAN [data/raw/olist_orders_dataset.csv]
            PROJECT 3/8 COLUMNS
            SELECTION: col("order_status") == "delivered"
            ESTIMATED ROWS: 99185
  PLAN 1:
    AGGREGATE[maintain_order: false]
      [len()] BY [col("order_purchase_timestamp").dt.truncate(["1mo"])]
      FROM
      simple π 1/1 ["order_purchase_timestamp"]
        CACHE[id: 94a1f8f2-2a94-42d2-bd92-7a93792805db]
END SINK_MULTIPLE
```

---

## 3. Reading it (bottom up)

1. **`Csv SCAN` appears once**, under `PLAN 0`. The file is read a single time.
2. **`PROJECT 3/8 COLUMNS`**: the union of what both queries need: `customer_id` (plan 0), `order_purchase_timestamp` (plan 1) and `order_status` (the shared filter).
3. **`SELECTION`**: the shared filter is pushed into the scan.
4. **`simple π 2/2`**: after filtering, `order_status` is dropped; the two needed columns stay.
5. **`CACHE[id: …]`**: the shared result is stored under an ID.
6. **`PLAN 1` points to the same `CACHE[id: …]`** and has no scan of its own. It reuses plan 0's work.
7. Each plan takes only its own column (`simple π 1/1`) and runs its own aggregation.
8. **`SINK_MULTIPLE`**: one execution, several outputs.

---

## 4. What to remember

- `collect_all` combines the plans into one before optimizing. That lets the optimizer see across queries.
- **Common subplan elimination**: identical sub-plans run once; Polars inserts the `CACHE` step itself. You did not call `cache()`.
- Projection and predicate pushdown still work across queries: the scan reads exactly the union of columns all queries need.
- Sharing needs parts to be **identical** (same source, same steps). Build shared parts once (like `base` above) and derive queries from it.
- Fully independent queries (different sources) gain parallelism only, not shared work.

---

## 5. Kitchen version

| Situation | Kitchen |
|---|---|
| `collect()` twice | two separate trips to the shop, chop the onions twice |
| `collect_all`, independent queries | two cooks side by side, each shopping for their own dish |
| `collect_all`, shared start | one trip, onions chopped once, two dishes served |
| Collect once into a variable | leftovers in the fridge |

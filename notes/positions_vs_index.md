# Positions vs index — learning notes

*Learned while working through Day 8. Builds on Day 4 (no index). Slicing in lazy mode comes back later in the series (slice pushdown).*

---

## 1. No index, but rows still have positions

Polars has no index. That does not mean rows have no order: every table still has **positions**, exactly like a Python list.

| | pandas index | Position |
|---|---|---|
| What it is | a label stored with the data | just "where the row sits right now" |
| Survives filter or sort? | yes, labels travel with their rows | no, positions are recounted from 0 every time |
| Can repeat or have gaps? | yes (`0, 5, 5, 12`) | never: always `0, 1, 2, …` |
| pandas access | `.loc[label]` | `.iloc[pos]` |
| Polars has it? | no | yes |

**Positions start at 0** because that is Python's convention: lists, tuples, NumPy arrays and pandas `.iloc` all count from 0. So the 10th row is position **9**.

**Example:**

```python
canceled = orders.filter(pl.col("order_status") == "canceled")
canceled.row(0)   # the first CANCELED order, whatever line it was in the file
```

In pandas, `.loc[0]` after the same filter may fail (label 0 may be gone); `.iloc[0]` gives the first remaining row. Polars only has the `.iloc` kind: position, recounted after every step.

---

## 2. Looking at a specific row or range

```python
df.row(9)                  # 10th row as a tuple
df.row(9, named=True)      # 10th row as a dict {column: value}, easier to read
df.slice(9, 1)             # 1-row DataFrame: start at 9, take 1
df[9]                      # same, bracket shortcut for a quick look

df.slice(9, 5)             # rows 10–14
df[9:14]                   # same

lf.slice(9, 1).collect()   # lazy: describe the slice, then collect
```

**`.item()`** takes the single value out of a 1×1 DataFrame (or a one-element Series) as a plain Python value. It raises an error if there is more than one value, a useful safety check:

```python
df.select(pl.col("order_approved_at").null_count()).item()   # just the number
```

---

## 3. When "row 10" is not reliable

- After `group_by`, `join` or a **streaming** lazy query, row order is **not guaranteed** (Day 7). "Row 10" can change between runs. Sort first if position matters.
- To find a specific record, use a **key**, not a position: `df.filter(pl.col("order_id") == "...")`.

---

## 4. Making positions permanent: `with_row_index`

```python
df = df.with_row_index("row_nr")   # current positions become a real column (0, 1, 2, ...)
```

Now the number travels with its row through later filters and sorts, much like a pandas index, but explicit, and only when you ask for it.

---

## 5. Brackets vs expressions, in one line

`df[9]`, `df[9:14]` and `df["col"]` take data **out** of an eager DataFrame right now. They do not exist on a LazyFrame. For work inside a query, use `slice`, `filter` and `pl.col`.

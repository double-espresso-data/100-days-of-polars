# Compute vs Memory — learning notes

*Learned while writing Day 3 (threads and engines). Possible future post.*

---

## 1. Compute vs memory, in general computing

Every program does two things: it **works on data** (compute) and **moves data to where the work happens** (memory). Speed depends on which of the two holds things up.

**Compute** is the CPU doing operations: add, compare, multiply, branch.

- Measured in clock speed (GHz) and operations per second.
- A modern core does billions of simple operations per second, and several per clock cycle.

**Memory** is where data sits while it isn't being worked on. It is a hierarchy: the closer to the core, the faster and the smaller.

| Level | Typical size | Rough time to fetch | Kitchen version |
|---|---|---|---|
| Registers | a few hundred bytes | under 1 ns | in the cook's hand |
| L1 cache | tens of KB per core | ~1 ns | on the cutting board |
| L2 cache | a few MB per core | ~4 ns | on the counter |
| L3 cache | tens of MB, shared | ~10–20 ns | the fridge in the kitchen |
| RAM | GBs | ~80–100 ns | the store room down the corridor |
| SSD | hundreds of GB to TBs | ~0.1 ms (100,000 ns) | a supplier across town |
| Network / cloud storage | unlimited | milliseconds | a delivery from another city |

**The key fact (the "memory wall"):** over the decades, CPUs got faster much more quickly than memory did. One trip to RAM takes as long as a few hundred operations. So most programs spend more time waiting for data than computing on it.

**What follows:**

- **Compute-bound:** the data is already close (registers, cache) and the CPU is busy all the time. Speed it up with faster or more cores, or better algorithms.
- **Memory-bound:** the CPU sits idle waiting for data. Speed it up by keeping data close and contiguous, reading less of it, and reading it in order so the CPU can fetch ahead.
- **Caches work best on data read in order.** The CPU fetches in chunks (cache lines of 64 bytes) and guesses what comes next. Contiguous data (an array, an Arrow buffer) fits that pattern. Scattered data (pointers to objects) defeats it.
- **Disk and network are a different league:** thousands to millions of times slower than RAM. That is why "read less", "skip what you don't need" and "don't spill unless you must" matter so much.

**One line to remember:** the CPU is rarely the slow part; getting data to it is. Fast software is mostly software that moves less data, and moves it in order.

---

## 2. Compute-bound vs memory-bound

**The core question:** what is the CPU waiting for?

| | Compute-bound | Memory-latency-bound | Memory-bandwidth-bound |
|---|---|---|---|
| **Bottleneck** | The core's maths units | Waiting for each piece of data to arrive | The memory bus is full |
| **Looks like** | Tight loops, heavy arithmetic, data already in cache | Scattered reads, pointer chasing, cache misses | Streaming through huge arrays |
| **Example** | Hashing, string parsing, sorting small data | pandas `object` columns, row-wise `apply` on Python objects | Summing a multi-GB column |
| **Hyper-Threading gain** | Small (units already busy) | Large (the other thread fills the waits) | Small (the bus is already full) |
| **More physical cores help?** | Yes, nearly linearly | Yes | Only until the bus fills up |
| **Fix** | Better algorithms, SIMD, more cores | Contiguous memory (Arrow), fewer pointers | Read less data: fewer columns, filters, smaller dtypes |

**Kitchen version:** compute-bound means the cook's hands are always busy. Latency-bound means the cook keeps waiting for ingredients from the store room. Bandwidth-bound means the corridor to the store room is jammed.

---

## 3. Hyper-Threading, and where Polars fits

**Do the two hyper-threads run at the same time?** Yes. The general term is *Simultaneous Multi-Threading*. A core has several execution units (integer maths, floating point, loading from memory), and one thread rarely keeps them all busy. With two threads, the core takes instructions from both in the same cycle, filling units the other left idle. But they share those units, the caches and the memory bandwidth, so when both need the same unit, one waits.

**Kitchen version:** the cook has a stove, a knife and an oven. With two dishes, the cook can chop for dish B while dish A simmers on the stove: real parallel work, not taking turns. If both dishes need the knife at the same moment, one waits.

**So, "two dishes on the go, but not twice the speed":** a hyper-threaded core typically does about 15–30% more work than the same core with one thread, not 100% more.

**What the second thread adds depends on the work:**

| Type of work | What the second thread adds | Why |
|---|---|---|
| Waits on memory a lot (scattered reads, cache misses) | A good gain | While thread A waits for data, thread B uses the idle units |
| Compute-heavy (tight maths loops) | Small, close to zero | Thread A already keeps the units busy |
| Bandwidth-limited (streaming huge arrays) | Small | The memory bus is already full |

Compute-heavy work is not *slow* with Hyper-Threading; it is about as fast as one thread per core. Hyper-Threading just does not add much (occasionally slightly less, from cache contention).

**Where Polars sits:** Polars stores data in contiguous Arrow buffers and runs tight loops over them, so its work is mostly compute- or bandwidth-bound, not latency-bound. Arrow turns latency-bound work (pandas `object` pointer chasing) into compute- or bandwidth-bound work. That is why Polars scales with physical cores, and why reading fewer bytes matters so much: projection pushdown, Parquet, smaller dtypes.

On my laptop (i5-1345U: 2 performance cores × 2 threads + 8 efficiency cores × 1 = 12 logical processors), Polars runs 12 threads. The 4 hyper-threads on the performance cores add a little; most of the real work comes from the 10 physical cores.

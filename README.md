## Large-Scale DBLP Graph Analysis & Streaming Algorithms

An efficient Python framework for processing, analyzing, and querying large-scale bibliographic networks derived from the **DBLP dataset**. This project demonstrates practical graph mining techniques, memory-efficient data structures, and randomized network algorithms.

---

## Project Overview

Analyzing massive network datasets requires balancing computational efficiency with memory limits. This project implements a complete pipeline that:
1. **Builds Bipartite Graphs:** Constructs dynamic author-publication graphs from raw publication CSVs (books, articles, proceedings, thesis, etc.).
2. **Builds K-Min Sketches:** Implements a deterministic **K-Min Hash** algorithm to estimate the number of unique authors and measure Jaccard similarity across publication categories in sub-linear time.
3. **Approximates Network Metrics:** Uses randomized Breadth-First Search (BFS) sampling to compute the average shortest path length on the **Largest Connected Component (LCC)**.

---

## Key Features & Engineering Highlights

* **Dynamic Graph Filtering:** Filters nodes and edges by publication year to analyze temporal network evolution.
* **Custom K-Min Sketch Implementation:** Built from scratch to support:
  * Cardinality estimation with varying sketch sizes ($k = 64, 128, 256, 512$).
  * Jaccard similarity estimation between author sets across files.
* **Randomized Distance Approximation:** Implements $\alpha$-$\epsilon$ bounded BFS sampling to estimate average distances with statistical guarantees.

---

## 📂 Project Structure

```text
.
├── progetto.py              # Main analysis script
├── out-dblp_*.csv           # DBLP publication datasets (Books, Articles, etc.)
└── README.md                # Project documentation

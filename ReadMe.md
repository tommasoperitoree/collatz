# 🌿 Collatz Conjecture Explorer

> *"The Collatz conjecture is the simplest open problem in all of mathematics."*  
> — Quoted often, source debated

[![Open in marimo](https://marimo.io/shield.svg)](https://marimo.app/github/tommasoperitoree/collatz/blob/main/collatz.py)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-blue?logo=github)](https://tommasoperitoree.github.io/collatz)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![marimo](https://img.shields.io/badge/notebook-marimo-EF4444)](https://marimo.io)

---

## What is this?

Take any positive integer. If it's even, divide it by 2. If it's odd, multiply by 3 and add 1. Repeat.  
The **Collatz conjecture** says you will always eventually reach 1 — nobody has ever proven it.

This project visualizes the paths of thousands of random starting numbers simultaneously, rendered as a fractal tree rooted at 1. Each branch turns **left for even nodes** (+8.65°) and **right for odd nodes** (−16°). Edge length shrinks logarithmically with node value. Color and thickness encode how many chains passed through each edge.

---

## Preview

![Collatz tree — 5000 paths below 1 million](preview.png)

*5,000 random starting points below 1,000,000 · rendered at 600 dpi*

---

## Interactive demo

**→ [Open live in browser](https://tommasoperitoree.github.io/collatz)** — no install, runs entirely in JavaScript

**→ [Open reactive notebook](https://marimo.app/github/tommasoperitoree/collatz/blob/main/collatz.py)** — full Python version via marimo's WASM runtime

---

## Run locally

```bash
pip install marimo matplotlib numpy
marimo edit collatz.py
```

The notebook has sliders for **N_STARTS** (100–10,000) and **MAX_VAL** (up to 10 million). Changes only apply when you click **▶ Run**, so you won't trigger expensive recomputes mid-slide.

---

## How the visualization works

| Parameter | Rule |
|---|---|
| Turn left | +8.65° for even nodes |
| Turn right | −16° for odd nodes |
| Edge length | `1 / log(node_value)` |
| Color | `log1p(traversal_count) / log1p(max_count)` via `magma` colormap |
| Line width | Proportional to same normalized count |

Bright yellow edges are "highways" — paths that thousands of chains share. Dark purple edges are barely visited.

---

## Files

| File | Description |
|---|---|
| `collatz.py` | Reactive marimo notebook |
| `index.html` | Self-contained browser demo (Canvas + JS) |
| `collatz-1million-5000.png` | High-res preview (600 dpi) |

---

## Notable numbers annotated

- **2¹⁹ = 524,288** — a pure power of 2, collapses to 1 in exactly 19 steps
- **837,799** — the number below 1,000,000 with the longest Collatz chain (524 steps)
- Top 3 branching nodes — the junctions most chains pass through

---

*Made with [marimo](https://marimo.io) · [matplotlib](https://matplotlib.org) · NumPy*
import marimo

__generated_with = "0.21.1"
app = marimo.App(width="wide")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    from collections import defaultdict, Counter

    return Counter, LineCollection, defaultdict, mo, np, plt


@app.cell
def _(mo):
    mo.md("""
    # 🌿 Collatz Conjecture Explorer
    """)
    return


@app.cell
def _(mo):
    n_starts_slider = mo.ui.slider(
        100, 10_000, value=5_000, step=100,
        label="Number of starting points"
    )
    max_val_dropdown = mo.ui.dropdown(
        options={
            "100 thousand":   100_000,
            "500 thousand":   500_000,
            "1 million":    1_000_000,
            "5 million":    5_000_000,
            "10 million":  10_000_000,
        },
        value="1 million",
        label="Max starting value",
    )
    mo.hstack([n_starts_slider, max_val_dropdown], justify="start", gap=2)
    return max_val_dropdown, n_starts_slider


@app.cell
def _(max_val_dropdown, mo, n_starts_slider, np):
    N_STARTS = n_starts_slider.value
    MAX_VAL  = max_val_dropdown.value

    with mo.status.spinner(title=f"Finding longest chain below {MAX_VAL:,}…"):

        def collatz_length(n):
            length = 0
            while n > 1:
                n = n // 2 if n % 2 == 0 else n * 3 + 1
                length += 1
            return length

        longest_start = max(range(1, MAX_VAL), key=collatz_length)
        longest_len   = collatz_length(longest_start)

    anchor = 1024 * 512

    np.random.seed(42)
    starts = np.random.choice(MAX_VAL, N_STARTS, replace=False)
    starts[:2] = [anchor, longest_start]
    return MAX_VAL, N_STARTS, anchor, longest_len, longest_start, starts


@app.cell
def _(
    MAX_VAL,
    N_STARTS,
    defaultdict,
    longest_len,
    longest_start,
    mo,
    np,
    starts,
):
    with mo.status.spinner(title="Building Collatz tree…"):
        edge_counts = defaultdict(int)
        for start in starts:
            position = int(start)
            while position > 1:
                position_new = position // 2 if position % 2 == 0 else position * 3 + 1
                edge_counts[(position_new, position)] += 1
                position = position_new

        chain = np.array(
            [[a, b, c] for (a, b), c in edge_counts.items()],
            dtype=np.int64,
        )
        chain = chain[np.argsort(chain[:, 0])]

    def fmt_max(n):
        if n >= 1_000_000_000: return f"{n // 1_000_000_000:,} billion"
        if n >= 1_000_000:     return f"{n // 1_000_000:,} million"
        return f"{n:,}"

    mo.callout(
        mo.md(
            f"**Tree built.** "
            f"{len(chain):,} unique edges — "
            f"longest chain: **{longest_start:,}** ({longest_len} steps) — "
            f"{N_STARTS:,} starts below {fmt_max(MAX_VAL)}"
        ),
        kind="success",
    )
    return chain, fmt_max


@app.cell
def _(
    Counter,
    LineCollection,
    MAX_VAL,
    N_STARTS,
    anchor,
    chain,
    defaultdict,
    fmt_max,
    longest_len,
    longest_start,
    mo,
    np,
    plt,
):
    with mo.status.spinner(title="Rendering tree…"):
        max_log_count = np.log1p(chain[:, 2].max())

        edges_from = defaultdict(list)
        for _i, (_dest, _src, _) in enumerate(chain):
            edges_from[int(_dest)].append((int(_src), _i))

        node_pos = {1: (0.0, 0.0, 0.0)}
        segments, colors, linewidths = [], [], []
        stack = [(1, np.array([0.0, 0.0]), 0.0)]

        while stack:
            _start, pos_beg, angle = stack.pop()
            for _src, _idx in edges_from[_start]:
                new_angle = (
                    angle + np.deg2rad(8.65) if _src % 2 == 0
                    else angle - np.deg2rad(16)
                )
                pos_end = pos_beg + np.array([np.cos(new_angle), np.sin(new_angle)]) / np.log(_src)
                col = np.log1p(chain[_idx, 2]) / max_log_count

                segments.append([pos_beg, pos_end])
                colors.append(plt.cm.magma(1 - col))
                linewidths.append(2 * col)

                node_pos[_src] = (pos_end[0], pos_end[1], col)
                stack.append((_src, pos_end, new_angle))

        fig, ax = plt.subplots(figsize=(10, 5.6), layout="constrained")
        ax.axis("off")
        fig.patch.set_facecolor("white")

        lc = LineCollection(segments, colors=colors, linewidths=linewidths, zorder=1)
        ax.add_collection(lc)
        ax.autoscale()

        # Anchor + longest-chain labels
        anchor_label  = f"2¹⁹ = {anchor:,}"
        longest_label = (
            f"{longest_start:,}\n"
            f"Longest chain below {fmt_max(MAX_VAL)}\n"
            f"({longest_len} steps)"
        )
        for _num, _label in zip([anchor, longest_start], [anchor_label, longest_label]):
            if _num in node_pos:
                _x, _y, _col = node_pos[_num]
                ax.text(_x - 0.1, _y + 0.1, _label, fontsize=6, fontname="Georgia",
                        ha="right", va="top", color=plt.cm.magma(1 - _col))

        # Top branching nodes
        branch_counts = Counter(int(_dest) for _dest, _src, _ in chain)
        top_nodes = [
            _n for _n, _ in branch_counts.most_common(8)
            if _n not in (1, anchor, longest_start)
        ][:3]
        for _num in top_nodes:
            if _num in node_pos:
                _x, _y, _col = node_pos[_num]
                ax.text(_x, _y - 0.4, f"{_num:,}", fontsize=6, fontname="Georgia",
                        ha="center", va="top", color=plt.cm.magma(1 - _col))

        ax.text(0, -0.4, "1", fontsize=6, ha="center", va="top", color=plt.cm.magma(0))

        # Title / subtitle / caption — all dynamic
        ax.text(10,  3,  "Collatz conjecture paths",
                fontname="Georgia", fontsize=16, color=plt.cm.magma(0.2))
        ax.text(10,  2,  f"for {N_STARTS:,} random starting points below {fmt_max(MAX_VAL)}",
                fontname="Georgia", fontsize=8,  color=plt.cm.magma(0.5))
        ax.text(10, -2,
            "Starting from the tree root, the path turns left by 8.65° to even nodes\n"
            "and right by 16° to odd nodes. The length of each edge scales as 1 over\n"
            "the logarithm of its node further from the root. The color and the thickness\n"
            "depend linearly on the log1p of how often the edge was traversed.",
            fontname="Georgia", fontsize=6, linespacing=1.4, color=plt.cm.magma(0.7))

        filename = f"collatz-{fmt_max(MAX_VAL).replace(' ', '')}-{N_STARTS}.png"
        plt.savefig(filename, dpi=600, facecolor="w")

    mo.vstack([
        mo.image(filename, width="100%"),
        mo.md(f"💾 Saved as `{filename}` at 600 dpi"),
    ])
    return


if __name__ == "__main__":
    app.run()

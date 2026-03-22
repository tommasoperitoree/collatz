import marimo

__generated_with = "0.21.1"
app = marimo.App()


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
def __(mo):
	n_starts_slider = mo.ui.slider(
		100, 10_000, value=5_000, step=100,
		label="Number of starting points"
	)
	max_val_dropdown = mo.ui.dropdown(
		options={
			"100 thousand":  100_000,
			"500 thousand":  500_000,
			"1 million":   1_000_000,
			"5 million":   5_000_000,
			"10 million": 10_000_000,
		},
		value="1 million",
		label="Max starting value",
	)
	run_button = mo.ui.run_button(label="▶ Run")
	mo.hstack([n_starts_slider, max_val_dropdown, run_button], justify="start", align="end", gap=2)
	return max_val_dropdown, n_starts_slider, run_button

@app.cell
def __(mo, run_button, n_starts_slider, max_val_dropdown, np):
	mo.stop(
		not run_button.value,
		mo.md("_Adjust parameters above and click **▶ Run**_")
	)
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
		if n >= 1_000_000:	 return f"{n // 1_000_000:,} million"
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
def __(
	Counter, LineCollection, MAX_VAL, N_STARTS, anchor, chain,
	defaultdict, fmt_max, longest_len, longest_start, mo, np, plt,
):
	FONT = "DejaVu Serif"
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

				r, g, b, _ = plt.cm.magma(1 - col)
				segments.append([pos_beg, pos_end])
				colors.append((r, g, b, max(0.15, col ** 0.5)))
				linewidths.append(2 * col)

				if col > 0.5:
					segments.append([pos_beg, pos_end])
					colors.append((r, g, b, 0.12 * col))
					linewidths.append(10 * col)

				node_pos[_src] = (pos_end[0], pos_end[1], col)
				stack.append((_src, pos_end, new_angle))

		fig, ax = plt.subplots(figsize=(10, 5.6), layout="constrained")
		ax.axis("off")
		fig.patch.set_facecolor("#0d0d0d")
		ax.set_facecolor("#0d0d0d")

		lc = LineCollection(segments, colors=colors, linewidths=linewidths, zorder=1)
		ax.add_collection(lc)
		ax.autoscale()

		# ── top_nodes defined FIRST ──────────────────────────────────────────
		branch_counts = Counter(int(_dest) for _dest, _src, _ in chain)
		top_nodes = [
			_n for _n, _ in branch_counts.most_common(8)
			if _n not in (1, anchor, longest_start)
		][:3]

		# ── Dot markers (can now reference top_nodes) ────────────────────────
		for _num in [anchor, longest_start] + top_nodes:
			if _num in node_pos:
				_x, _y, _col = node_pos[_num]
				_r, _g, _b, _ = plt.cm.magma(1 - _col)
				ax.scatter([_x], [_y], s=18, color=(_r, _g, _b), zorder=5, linewidths=0)
				ax.scatter([_x], [_y], s=50, color=(_r, _g, _b, 0.2), zorder=4, linewidths=0)

		# ── Labels ───────────────────────────────────────────────────────────
		anchor_label  = f"2¹⁹ = {anchor:,}"
		longest_label = (
			f"{longest_start:,}\n"
			f"Longest chain below {fmt_max(MAX_VAL)}\n"
			f"({longest_len} steps)"
		)
		for _num, _label in zip([anchor, longest_start], [anchor_label, longest_label]):
			if _num in node_pos:
				_x, _y, _col = node_pos[_num]
				ax.text(_x - 0.1, _y + 0.1, _label, fontsize=6, fontfamily=FONT,
						ha="right", va="top", color=plt.cm.magma(1 - _col))

		for _num in top_nodes:
			if _num in node_pos:
				_x, _y, _col = node_pos[_num]
				ax.text(_x, _y - 0.4, f"{_num:,}", fontsize=6, fontfamily=FONT,
						ha="center", va="top", color=plt.cm.magma(1 - _col))

		# ── Highway spine labels ─────────────────────────────────────────────────────
		# Walk from root following the highest-count outgoing edge at each step
		# This traces the "main trunk" of the tree
		highway_nodes = []
		current = 1
		for _ in range(80):  # max 80 steps along the spine
			children = edges_from.get(current, [])
			if not children:
				break
			# pick the child with the highest traversal count
			best_src, best_idx = max(children, key=lambda c: chain[c[1], 2])
			highway_nodes.append(best_src)
			current = best_src

		# Label every ~12th node along the highway (skip ones too close to other labels)
		labeled = {1, anchor, longest_start} | set(top_nodes)
		for i, node in enumerate(highway_nodes):
			if i % 12 != 0:
				continue
			if node in labeled:
				continue
			if node not in node_pos:
				continue
			_x, _y, _col = node_pos[node]
			ax.annotate(
		    	f"{node:,}",
		    	xy=(_x, _y),
		    	xytext=(_x + 0.3, _y + 0.15),
		        fontsize=5,
		        fontfamily=FONT,
		        color=plt.cm.magma(max(0.4, 1 - _col)),
		        arrowprops=dict(
		            arrowstyle="-",
		            color=plt.cm.magma(max(0.4, 1 - _col)),
		            lw=0.5,
		            alpha=0.6,
		        ),
		        ha="left",
		        va="bottom",
		    )
			labeled.add(node)

			
		ax.text(0, -0.4, "1", fontsize=6, ha="center", va="top",
				color=plt.cm.magma(0.9))

		# ── Title / subtitle / caption ───────────────────────────────────────
		ax.text(10,  3, "Collatz conjecture paths",
				fontfamily=FONT, fontsize=16, color=plt.cm.magma(0.95))
		ax.text(10,  2, f"for {N_STARTS:,} random starting points below {fmt_max(MAX_VAL)}",
				fontfamily=FONT, fontsize=8,  color=plt.cm.magma(0.75))
		ax.text(10, -2,
			"Starting from the tree root, the path turns left by 8.65° to even nodes\n"
			"and right by 16° to odd nodes. The length of each edge scales as 1 over\n"
			"the logarithm of its node further from the root. The color and the thickness\n"
			"depend linearly on the log1p of how often the edge was traversed.",
			fontfamily=FONT, fontsize=6, linespacing=1.4, color=plt.cm.magma(0.55))

		filename = f"collatz-{fmt_max(MAX_VAL).replace(' ', '')}-{N_STARTS}.png"
		import io, base64
		buf = io.BytesIO()
		fig.savefig(buf, format='png', dpi=150, facecolor="#0d0d0d")
		buf.seek(0)
		img_b64 = base64.b64encode(buf.read()).decode()
		plt.close(fig)

	mo.vstack([
	    mo.Html(f'<img src="data:image/png;base64,{img_b64}" style="width:100%;border-radius:8px">'),
	    mo.md(f"💾 Saved as `{filename}` at 600 dpi"),
	])
	

if __name__ == "__main__":
	app.run()

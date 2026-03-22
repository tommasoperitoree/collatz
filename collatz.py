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
def _(mo):
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
	mo.hstack([n_starts_slider, max_val_dropdown, run_button],
			  justify="start", align="end", gap=2)
	return max_val_dropdown, n_starts_slider, run_button


@app.cell
def _(max_val_dropdown, mo, n_starts_slider, np, run_button):
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
	import io, base64, os

	FONT = "DejaVu Serif"
	BG   = "#0d0d0d"

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

				# ── FIXED: magma(col) not magma(1-col) on dark background ──
				# col=1 (highway) → magma(1) = bright yellow  ✓
				# col=0 (cold)	→ magma(0) = near-black, lifted by floor
				r, g, b, _ = plt.cm.magma(col)
				alpha = 0.45 + col * 0.55	# floor raised from 0.3 → 0.45
				lw	= max(0.8, 2.5 * col)  # floor raised from 0.5 → 0.8	   # floor 0.5px

				segments.append([pos_beg, pos_end])
				colors.append((r, g, b, alpha))
				linewidths.append(lw)

				# Glow layer for hot edges
				if col > 0.55:
					segments.append([pos_beg, pos_end])
					colors.append((r, g, b, 0.10 * col))
					linewidths.append(12 * col)

				node_pos[_src] = (pos_end[0], pos_end[1], col)
				stack.append((_src, pos_end, new_angle))

		fig, ax = plt.subplots(figsize=(10, 5.6), layout="constrained")
		ax.axis("off")
		fig.patch.set_facecolor(BG)
		ax.set_facecolor(BG)

		lc = LineCollection(segments, colors=colors, linewidths=linewidths, zorder=1)
		ax.add_collection(lc)
		ax.autoscale()

		# ── Top branching nodes ───────────────────────────────────────────
		branch_counts = Counter(int(_dest) for _dest, _src, _ in chain)
		top_nodes = [
			_n for _n, _ in branch_counts.most_common(8)
			if _n not in (1, anchor, longest_start)
		][:3]

		# ── Dot markers ───────────────────────────────────────────────────
		for _num in [anchor, longest_start] + top_nodes:
			if _num in node_pos:
				_x, _y, _col = node_pos[_num]
				_r, _g, _b, _ = plt.cm.magma(max(0.65,_col))
				ax.scatter([_x], [_y], s=20, color=(_r, _g, _b), zorder=5, linewidths=0)
				ax.scatter([_x], [_y], s=60, color=(_r, _g, _b, 0.2), zorder=4, linewidths=0)

		# ── Highlight strands to annotated nodes ─────────────────────────────────
		for _num in [anchor, longest_start] + top_nodes:
			if _num not in node_pos:
				continue
			# Walk the ACTUAL Collatz sequence from this node to 1
			# instead of following highest-traffic edges (that traces the highway)
			_cur = _num
			while _cur > 1:
				_next = _cur // 2 if _cur % 2 == 0 else _cur * 3 + 1
				if _cur not in node_pos or _next not in node_pos:
					break
				_x1, _y1, _ = node_pos[_cur]
				_x2, _y2, _ = node_pos[_next]
				_r, _g, _b, _ = plt.cm.magma(0.7)
				ax.plot([_x1, _x2], [_y1, _y2],
						color=(_r, _g, _b, 0.4),
						lw=1.2,
						zorder=3,
						solid_capstyle='round')
				_cur = _next

		# ── Named labels ──────────────────────────────────────────────────
		anchor_label  = f"2¹⁹ = {anchor:,}"
		longest_label = (
			f"{longest_start:,}\n"
			f"Longest chain below {fmt_max(MAX_VAL)}\n"
			f"({longest_len} steps)"
		)
		for _num, _label in zip([anchor, longest_start], [anchor_label, longest_label]):
			if _num in node_pos:
				_x, _y, _col = node_pos[_num]
				_r, _g, _b, _ = plt.cm.magma(max(0.7, _col))   # ← floor
				ax.text(_x - 0.1, _y + 0.1, _label, fontsize=6, fontfamily=FONT, ha="right", va="top", color=(_r, _g, _b))
		for _num in top_nodes:
			if _num in node_pos:
				_x, _y, _col = node_pos[_num]
				_r, _g, _b, _ = plt.cm.magma(max(0.65,_col))
				ax.text(_x, _y - 0.4, f"{_num:,}", fontsize=6, fontfamily=FONT,
						ha="center", va="top", color=(_r, _g, _b))

		# ── Highway spine labels ──────────────────────────────────────────
		highway_nodes = []
		current = 1
		for _ in range(80):
			children = edges_from.get(current, [])
			if not children:
				break
			best_src, best_idx = max(children, key=lambda c: chain[c[1], 2])
			highway_nodes.append(best_src)
			current = best_src

		labeled = {1, anchor, longest_start} | set(top_nodes)
		for i, node in enumerate(highway_nodes):
			if i % 12 != 0:
				continue
			if node in labeled or node not in node_pos:
				continue
			_x, _y, _col = node_pos[node]
			_r, _g, _b, _ = plt.cm.magma(max(0.5, _col))   # min brightness 0.5
			ax.annotate(
				f"{node:,}",
				xy=(_x, _y),
				xytext=(_x + 0.5, _y - 0.35),
				fontsize=5,
				fontfamily=FONT,
				color=(_r, _g, _b),
				arrowprops=dict(
					arrowstyle="-",
					color=(_r, _g, _b),
					lw=0.5,
					alpha=0.7,
				),
				ha="left",
				va="top",
			)
			labeled.add(node)

		# ── Root label ────────────────────────────────────────────────────
		_r, _g, _b, _ = plt.cm.magma(0.85)
		ax.text(0, -0.4, "1", fontsize=6, ha="center", va="top", color=(_r, _g, _b))

		# ── Title / subtitle / caption ────────────────────────────────────
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

		# ── Save ──────────────────────────────────────────────────────────
		import os
		NOTEBOOK_DIR = os.path.dirname(os.path.abspath(__file__))
		filename	 = os.path.join(NOTEBOOK_DIR,
						   f"collatz-{fmt_max(MAX_VAL).replace(' ', '')}-{N_STARTS}.png")
		preview_path = os.path.join(NOTEBOOK_DIR, "preview.png")

		# uncomment to update preview fig
		# fig.savefig(filename,	  dpi=600, facecolor=BG)
		# fig.savefig(preview_path,  dpi=600, facecolor=BG)

		# Lightweight inline version
		buf = io.BytesIO()
		fig.savefig(buf, format='png', dpi=150, facecolor=BG)
		buf.seek(0)
		img_b64 = base64.b64encode(buf.read()).decode()
		plt.close(fig)

	mo.vstack([
		mo.Html(f'<img src="data:image/png;base64,{img_b64}" style="width:100%;border-radius:8px">'),
		mo.md(f"💾 `{os.path.basename(filename)}` and `preview.png` saved at 600 dpi"),
	])
	return


if __name__ == "__main__":
	app.run()

"""
Gap Hunter 2 — Compact Architecture Diagram (16:9 PPT-friendly)

True left-to-right 16:9 layout:
  INPUT  →  PHASE 1  →  PHASE 2  →  PHASE 3  →  OUTPUT
  Shared Infrastructure spans the bottom

Run with:
    uv run docs/generate_architecture_compact.py
"""

from graphviz import Digraph

FONT = "Helvetica-Bold"

COLORS = {
    "input": "#2980B9",
    "p1": "#27AE60",
    "p2": "#D35400",
    "p3": "#7D3C98",
    "output": "#C0392B",
    "infra": "#566573",
}

BG = {
    "input": "#D6EAF8",
    "p1": "#D5F5E3",
    "p2": "#FDEBD0",
    "p3": "#E8DAEF",
    "output": "#FADBD8",
    "infra": "#EAECEE",
}


def node(g, name, label, color, bg, shape="box", fontsize="18"):
    g.node(
        name,
        label=label,
        shape=shape,
        style="filled,rounded",
        fillcolor=bg,
        color=color,
        fontname=FONT,
        fontsize=fontsize,
        fontcolor="#1A1A2E",
        margin="0.30,0.20",
        penwidth="2.8",
        width="3.0",
        height="0.9",
    )


def infra_node(g, name, label, color, bg, fontsize="17"):
    g.node(
        name,
        label=label,
        shape="box",
        style="filled,rounded",
        fillcolor=bg,
        color=color,
        fontname=FONT,
        fontsize=fontsize,
        fontcolor="#1A1A2E",
        margin="0.30,0.20",
        penwidth="2.5",
        width="3.8",
        height="0.85",
    )


def arrow(g, a, b, color, style="solid", bold=False):
    g.edge(
        a,
        b,
        color=color,
        fontname=FONT,
        style=style,
        penwidth="3.0" if bold else "1.8",
        arrowsize="0.9",
    )


def build():
    g = Digraph("gap_hunter_16x9", format="png")
    g.attr(
        rankdir="LR",
        splines="polyline",
        nodesep="0.5",
        ranksep="1.6",
        fontname=FONT,
        bgcolor="white",
        pad="0.6",
        dpi="200",
        compound="true",
        # 16:9 canvas — wide and short
        size="20,11.25!",
        ratio="fill",
    )
    g.attr("node", fontname=FONT)
    g.attr("edge", fontname=FONT)

    # ── COLUMN 1: INPUT ──────────────────────────────────────────────────────
    with g.subgraph(name="cluster_input") as c:
        c.attr(
            label="INPUT",
            style="filled,rounded",
            fillcolor=BG["input"],
            color=COLORS["input"],
            fontname=FONT,
            fontsize="20",
            fontcolor=COLORS["input"],
        )
        node(
            c,
            "pdf_in",
            "Policy PDF\n(ISO / NIST / Any)",
            COLORS["input"],
            BG["input"],
            shape="note",
            fontsize="18",
        )

    # ── COLUMN 2: PHASE 1 ────────────────────────────────────────────────────
    with g.subgraph(name="cluster_p1") as c:
        c.attr(
            label="Phase 1 · Extract",
            style="filled,rounded",
            fillcolor=BG["p1"],
            color=COLORS["p1"],
            fontname=FONT,
            fontsize="20",
            fontcolor=COLORS["p1"],
        )
        node(c, "p1_pdf", "PDF → Markdown\n(Docling)", COLORS["p1"], BG["p1"])
        node(c, "p1_head", "Heading Detection\n(Regex / LLM)", COLORS["p1"], BG["p1"])
        node(c, "p1_ext", "Extract · Validate\nSummarize", COLORS["p1"], BG["p1"])

    # ── COLUMN 3: PHASE 2 ────────────────────────────────────────────────────
    with g.subgraph(name="cluster_p2") as c:
        c.attr(
            label="Phase 2 · Gap Analysis",
            style="filled,rounded",
            fillcolor=BG["p2"],
            color=COLORS["p2"],
            fontname=FONT,
            fontsize="20",
            fontcolor=COLORS["p2"],
        )
        node(
            c, "p2_scope", "Scope Classifier\n6 NIST Functions", COLORS["p2"], BG["p2"]
        )
        node(
            c,
            "p2_map",
            "MAP — Evidence Scan\nSection × Subcategory",
            COLORS["p2"],
            BG["p2"],
        )
        node(c, "p2_red", "REDUCE — Assess\nStatus · Gap · Fix", COLORS["p2"], BG["p2"])
        node(c, "p2_sum", "Summaries\n+ Maturity Score", COLORS["p2"], BG["p2"])

    # ── COLUMN 4: PHASE 3 ────────────────────────────────────────────────────
    with g.subgraph(name="cluster_p3") as c:
        c.attr(
            label="Phase 3 · Revise Policy",
            style="filled,rounded",
            fillcolor=BG["p3"],
            color=COLORS["p3"],
            fontname=FONT,
            fontsize="20",
            fontcolor=COLORS["p3"],
        )
        node(c, "p3_tgt", "Gap Targeter\nModify / New Section", COLORS["p3"], BG["p3"])
        node(c, "p3_add", "Addition Writer\n+ CoVe Verify", COLORS["p3"], BG["p3"])
        node(c, "p3_int", "Integration Editor\n(RAPTOR Merge)", COLORS["p3"], BG["p3"])
        node(c, "p3_road", "Roadmap Planner\n+ Validator", COLORS["p3"], BG["p3"])

    # ── COLUMN 5: OUTPUT ─────────────────────────────────────────────────────
    with g.subgraph(name="cluster_out") as c:
        c.attr(
            label="OUTPUT",
            style="filled,rounded",
            fillcolor=BG["output"],
            color=COLORS["output"],
            fontname=FONT,
            fontsize="20",
            fontcolor=COLORS["output"],
        )
        node(
            c,
            "out_rep",
            "Gap Report\n+ Executive Summary",
            COLORS["output"],
            BG["output"],
            shape="note",
        )
        node(
            c,
            "out_pol",
            "Revised Policy\nDocument",
            COLORS["output"],
            BG["output"],
            shape="note",
        )
        node(
            c,
            "out_road",
            "Improvement\nRoadmap",
            COLORS["output"],
            BG["output"],
            shape="note",
        )

    # ── BOTTOM BAND: SHARED INFRA ─────────────────────────────────────────────
    with g.subgraph(name="cluster_infra") as c:
        c.attr(
            label="Shared Infrastructure  (used across all phases)",
            style="filled,rounded",
            fillcolor=BG["infra"],
            color=COLORS["infra"],
            fontname=FONT,
            fontsize="18",
            fontcolor=COLORS["infra"],
        )
        # force same rank so they sit side-by-side in a row
        with c.subgraph() as s:
            s.attr(rank="same")
            infra_node(
                s,
                "llm_box",
                "Local LLM\nGemma 4 2B · Offline · 32K ctx",
                COLORS["infra"],
                BG["infra"],
            )
            infra_node(
                s,
                "nist_box",
                "NIST Knowledge Base\nCSF 2.0 · 36 CIS Templates",
                COLORS["infra"],
                BG["infra"],
            )
            infra_node(
                s,
                "val_box",
                "Evaluator-Optimizer\nGenerate → Validate → Retry ×3",
                COLORS["infra"],
                BG["infra"],
            )

    # ── MAIN PIPELINE ARROWS (bold, left→right) ───────────────────────────────
    P1, P2, P3 = COLORS["p1"], COLORS["p2"], COLORS["p3"]

    arrow(g, "pdf_in", "p1_pdf", COLORS["input"], bold=True)
    arrow(g, "p1_pdf", "p1_head", P1, bold=True)
    arrow(g, "p1_head", "p1_ext", P1, bold=True)
    arrow(g, "p1_ext", "p2_scope", P2, bold=True)
    arrow(g, "p2_scope", "p2_map", P2, bold=True)
    arrow(g, "p2_map", "p2_red", P2, bold=True)
    arrow(g, "p2_red", "p2_sum", P2, bold=True)
    arrow(g, "p2_sum", "p3_tgt", P3, bold=True)
    arrow(g, "p3_tgt", "p3_add", P3, bold=True)
    arrow(g, "p3_add", "p3_int", P3, bold=True)
    arrow(g, "p3_int", "p3_road", P3, bold=True)
    arrow(g, "p3_road", "out_rep", COLORS["output"], bold=True)
    arrow(g, "p3_int", "out_pol", COLORS["output"], bold=True)
    arrow(g, "p3_road", "out_road", COLORS["output"], bold=True)

    # ── INFRA DASHED CONNECTIONS ──────────────────────────────────────────────
    IN = COLORS["infra"]
    arrow(g, "llm_box", "p1_ext", IN, style="dashed")
    arrow(g, "llm_box", "p2_map", IN, style="dashed")
    arrow(g, "llm_box", "p3_add", IN, style="dashed")
    arrow(g, "nist_box", "p2_scope", IN, style="dashed")
    arrow(g, "nist_box", "p3_add", IN, style="dashed")
    arrow(g, "val_box", "p1_ext", IN, style="dashed")
    arrow(g, "val_box", "p2_sum", IN, style="dashed")
    arrow(g, "val_box", "p3_int", IN, style="dashed")

    return g


if __name__ == "__main__":
    import os

    g = build()
    out = os.path.join(os.path.dirname(__file__), "architecture_compact")
    rendered = g.render(out, cleanup=True)
    print(f"Saved: {rendered}")

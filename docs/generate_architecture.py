"""
Gap Hunter 2 — Architecture Diagram Generator

Three strictly-separated columns: Phase 1 | Phase 2 | Phase 3
with Infrastructure and NIST Knowledge Base as top/bottom bands.

Run with:
    uv run docs/generate_architecture.py
"""

from graphviz import Digraph

FONT = "Helvetica"

# Colour palette
FILL = {
    "entry": "#E3F2FD",  # pale blue   — orchestrators
    "agent": "#F3E5F5",  # pale purple — LLM agents
    "tool": "#E8F5E9",  # pale green  — tools / config
    "file": "#FCE4EC",  # pale pink   — file outputs
    "util": "#FFF3E0",  # pale orange — shared utilities
    "data": "#FFF8E1",  # pale amber  — data stores
}
BORDER = {
    "p1": "#1565C0",
    "p2": "#2E7D32",
    "p3": "#6A1B9A",
    "infra": "#37474F",
    "nist": "#BF360C",
}
CLUSTER_BG = {
    "p1": "#E3F2FD",
    "p2": "#E8F5E9",
    "p3": "#F3E5F5",
    "infra": "#ECEFF1",
    "nist": "#FBE9E7",
    "cli": "#E8EAF6",
}


def n(g, name, label, fill, border, shape="box"):
    """Add a styled node."""
    g.node(
        name,
        label=label,
        shape=shape,
        style="filled,rounded",
        fillcolor=fill,
        color=border,
        fontname=FONT,
        fontsize="10",
        margin="0.12,0.07",
    )


def e(g, a, b, label="", color="#607D8B", style="solid", pw="1.1", arr="normal"):
    """Add a styled edge using xlabel to avoid routing conflicts."""
    g.edge(
        a,
        b,
        xlabel=label,
        color=color,
        fontcolor="#424242",
        fontname=FONT,
        fontsize="8",
        style=style,
        penwidth=pw,
        arrowsize="0.65",
        arrowhead=arr,
    )


def build() -> Digraph:
    g = Digraph("gap_hunter", format="png")
    g.attr(
        rankdir="TB",
        splines="polyline",
        nodesep="0.55",
        ranksep="0.9",
        fontname=FONT,
        bgcolor="white",
        pad="0.5",
        dpi="160",
        compound="true",
    )
    g.attr("node", fontname=FONT)
    g.attr("edge", fontname=FONT)

    # ── Title ────────────────────────────────────────────────────────────────
    g.node(
        "TITLE",
        label="Gap Hunter 2\nNIST CSF Policy Gap Analysis Engine",
        shape="plaintext",
        fontsize="18",
        fontname=FONT,
        fontcolor="#1A237E",
    )

    # ════════════════════════════════════════════════════════════════════════
    # CLI
    # ════════════════════════════════════════════════════════════════════════
    with g.subgraph(name="cluster_cli") as c:
        c.attr(
            label="CLI  (main.py)",
            style="filled,rounded",
            fillcolor=CLUSTER_BG["cli"],
            color="#3949AB",
            fontname=FONT,
            fontsize="11",
        )
        n(c, "main", "main()", FILL["entry"], BORDER["infra"])
        n(c, "run_ext", "run_extraction()", FILL["entry"], BORDER["p1"])
        n(c, "run_ana", "run_analysis()", FILL["entry"], BORDER["p2"])
        n(
            c,
            "run_rev",
            "run_revision()\n--revision-only flag\nskips Phase 1+2",
            FILL["entry"],
            BORDER["p3"],
        )

    # ════════════════════════════════════════════════════════════════════════
    # NIST Knowledge Base
    # ════════════════════════════════════════════════════════════════════════
    with g.subgraph(name="cluster_nist") as c:
        c.attr(
            label="NIST Knowledge Base",
            style="filled,rounded",
            fillcolor=CLUSTER_BG["nist"],
            color=BORDER["nist"],
            fontname=FONT,
            fontsize="11",
        )
        n(
            c,
            "nist_cfg",
            "nist_config.yaml\n106 subcategories (6 functions)\nguidance · questions · policies",
            FILL["tool"],
            BORDER["nist"],
        )
        n(
            c,
            "framework",
            "framework-documents/\n36 CIS MS-ISAC policy templates",
            FILL["tool"],
            BORDER["nist"],
        )
        n(
            c,
            "gap_tools",
            "gap_analysis_tools.py\nget_function_subcategories()\nget_framework_excerpt(max=600 chars)",
            FILL["tool"],
            BORDER["nist"],
        )

    # ════════════════════════════════════════════════════════════════════════
    # Infrastructure
    # ════════════════════════════════════════════════════════════════════════
    with g.subgraph(name="cluster_infra") as c:
        c.attr(
            label="Infrastructure  (shared across all phases)",
            style="filled,rounded",
            fillcolor=CLUSTER_BG["infra"],
            color=BORDER["infra"],
            fontname=FONT,
            fontsize="11",
        )
        n(
            c,
            "llm",
            "llm.py\nChatLlamaCpp singleton\nKey-based cache · n_ctx=32K",
            FILL["util"],
            BORDER["infra"],
        )
        n(
            c,
            "txt_sum",
            "text_summarizer.py\nsummarize_lossless(text, threshold)\n"
            "Summarize → Validate → Retry (max 3)\nkey_points ≤ 15 · summary ≤ 2000 chars",
            FILL["util"],
            BORDER["infra"],
        )

    # ════════════════════════════════════════════════════════════════════════
    # PHASE 1 — Extraction
    # ════════════════════════════════════════════════════════════════════════
    with g.subgraph(name="cluster_p1") as p1:
        p1.attr(
            label="Phase 1 — Section Extraction",
            style="filled,rounded",
            fillcolor=CLUSTER_BG["p1"],
            color=BORDER["p1"],
            fontname=FONT,
            fontsize="12",
        )

        n(p1, "pdf", "tools/pdf.py\nDocling PDF → Markdown", FILL["tool"], BORDER["p1"])
        n(
            p1,
            "hdet",
            "heading_detector.py\nRule-based (5 regex patterns)\nFast path: ≥2 headings found",
            FILL["tool"],
            BORDER["p1"],
        )
        n(
            p1,
            "extractor",
            "extractor.py\nextract_all_sections()\nSliding-window orchestrator",
            FILL["entry"],
            BORDER["p1"],
        )

        with p1.subgraph(name="cluster_p1_agents") as a:
            a.attr(
                label="Extraction Agents  (Evaluator-Optimizer per window)",
                style="dashed",
                color=BORDER["p1"],
                fontname=FONT,
                fontsize="10",
            )
            n(
                a,
                "ag1",
                "Agent 1: extractor_agent.py\nIdentify section boundaries\n→ ExtractionResult",
                FILL["agent"],
                BORDER["p1"],
            )
            n(
                a,
                "ag2",
                "Agent 2: validator_agent.py\nCheck boundary correctness\n→ ValidationResult",
                FILL["agent"],
                BORDER["p1"],
            )
            n(
                a,
                "ag3",
                "Agent 3: corrector_agent.py\nFix boundary errors\n→ ExtractionResult (corrected)",
                FILL["agent"],
                BORDER["p1"],
            )
            n(
                a,
                "ag4",
                "Agent 4: summarizer_agent.py\nSummarize section content\n→ SummarizationResult",
                FILL["agent"],
                BORDER["p1"],
            )

        n(
            p1,
            "f_sec",
            "sections_output.json\nFull section text",
            FILL["file"],
            BORDER["p1"],
            shape="cylinder",
        )
        n(
            p1,
            "f_mst",
            "master_list.json\nSection summaries",
            FILL["file"],
            BORDER["p1"],
            shape="cylinder",
        )

    # ════════════════════════════════════════════════════════════════════════
    # PHASE 2 — Gap Analysis
    # ════════════════════════════════════════════════════════════════════════
    with g.subgraph(name="cluster_p2") as p2:
        p2.attr(
            label="Phase 2 — NIST CSF Gap Analysis",
            style="filled,rounded",
            fillcolor=CLUSTER_BG["p2"],
            color=BORDER["p2"],
            fontname=FONT,
            fontsize="12",
        )

        n(
            p2,
            "gap_ana",
            "gap_analyzer.py\nrun_gap_analysis()\nPhase 2 orchestrator",
            FILL["entry"],
            BORDER["p2"],
        )

        with p2.subgraph(name="cluster_p2_scope") as s:
            s.attr(
                label="Step 1 — Policy Scope  (1 LLM call)",
                style="dashed",
                color=BORDER["p2"],
                fontname=FONT,
                fontsize="10",
            )
            n(
                s,
                "fn_cls",
                "classify_policy_functions()\n→ PolicyScopeClassification\nWhich of 6 functions are relevant?",
                FILL["agent"],
                BORDER["p2"],
            )

        with p2.subgraph(name="cluster_p2_mr") as m:
            m.attr(
                label="Steps 2+3 — Map-Reduce  (per in-scope subcategory)",
                style="dashed",
                color=BORDER["p2"],
                fontname=FONT,
                fontsize="10",
            )
            n(
                m,
                "sub_cls",
                "Subcategory Scope Classifier\n→ ScopeClassification\nin_scope_ids: list[str]",
                FILL["agent"],
                BORDER["p2"],
            )
            n(
                m,
                "map_ph",
                "MAP phase\n_map_one_section() × N sections\n→ SectionEvidenceResult\n(evidence snippets only)",
                FILL["agent"],
                BORDER["p2"],
            )
            n(
                m,
                "red_ph",
                "REDUCE phase\n_reduce_to_assessment()\n→ SubcategoryAssessment\nstatus · gap · recommendation",
                FILL["agent"],
                BORDER["p2"],
            )

        with p2.subgraph(name="cluster_p2_sum") as su:
            su.attr(
                label="Step 4 — Summaries  (Evaluator-Optimizer loops)",
                style="dashed",
                color=BORDER["p2"],
                fontname=FONT,
                fontsize="10",
            )
            n(
                su,
                "fn_sum",
                "function_summarizer_agent.py\nrun_summarize_with_validation()\n"
                "CODE stats + LLM executive summary\n→ FunctionGapSummary",
                FILL["agent"],
                BORDER["p2"],
            )
            n(
                su,
                "mst_sum",
                "run_master_summarize_with_validation()\n→ MasterGapSummary\nOverall maturity · top gaps",
                FILL["agent"],
                BORDER["p2"],
            )
            n(
                su,
                "consol",
                "build_consolidated_report()\nCODE ONLY — no LLM\nAggregated stats + 3-tier overview",
                FILL["tool"],
                BORDER["p2"],
            )

        n(
            p2,
            "f_ass",
            "assessments.json\ndict[fn → list[SubcategoryAssessment]]",
            FILL["data"],
            BORDER["p2"],
            shape="cylinder",
        )
        n(
            p2,
            "f_rpts",
            "6× {fn}_gap_analysis.md\n6× {fn}_gap_summary.md\nconsolidated + master",
            FILL["file"],
            BORDER["p2"],
            shape="cylinder",
        )

    # ════════════════════════════════════════════════════════════════════════
    # PHASE 3 — Policy Revision + Roadmap
    # ════════════════════════════════════════════════════════════════════════
    with g.subgraph(name="cluster_p3") as p3:
        p3.attr(
            label="Phase 3 — Policy Revision + Roadmap  (RAPTOR + CoVe)",
            style="filled,rounded",
            fillcolor=CLUSTER_BG["p3"],
            color=BORDER["p3"],
            fontname=FONT,
            fontsize="12",
        )

        n(
            p3,
            "pol_rev",
            "policy_reviser.py\nrun_policy_revision()\nPhase 3 orchestrator",
            FILL["entry"],
            BORDER["p3"],
        )
        n(
            p3,
            "gap_tgt",
            "parse_gap_targets()\nclassify_gap_target() — 1 LLM call/gap\n→ list[GapTarget]  (modify | new_section)",
            FILL["agent"],
            BORDER["p3"],
        )

        with p3.subgraph(name="cluster_phA") as a:
            a.attr(
                label="Phase A — Addition Collection  (per NIST function)",
                style="dashed",
                color=BORDER["p3"],
                fontname=FONT,
                fontsize="10",
            )
            n(
                a,
                "add_w",
                "Addition Writer\nrun_write_addition()\n→ AdditionBlock\n(delta only — never full section)",
                FILL["agent"],
                BORDER["p3"],
            )
            n(
                a,
                "cove_q",
                "CoVe Questioner\n_generate_verification_questions()\n→ 3-5 yes/no questions\n(from gap text only)",
                FILL["agent"],
                BORDER["p3"],
            )
            n(
                a,
                "cove_v",
                "CoVe Verifier\n_verify_one_question() × N\n→ VerificationQuestion\n1 LLM call per question",
                FILL["agent"],
                BORDER["p3"],
            )
            n(
                a,
                "clust_s",
                "RAPTOR Level-1\nrun_cluster_summarizer()\n→ ClusterSummary\n(compact prior-additions context)",
                FILL["agent"],
                BORDER["p3"],
            )

        with p3.subgraph(name="cluster_phB") as b:
            b.attr(
                label="Phase B — Integration  (once per section)",
                style="dashed",
                color=BORDER["p3"],
                fontname=FONT,
                fontsize="10",
            )
            n(
                b,
                "int_ed",
                "RAPTOR Root: Integration Editor\nrun_integration_pass()\n→ IntegrationResult\noriginal + all blocks merged",
                FILL["agent"],
                BORDER["p3"],
            )
            n(
                b,
                "int_val",
                "Integration Validator\nvalidate_integration()\nCODE: ID coverage check\nLLM: coherence (first 1500 chars)",
                FILL["agent"],
                BORDER["p3"],
            )

        with p3.subgraph(name="cluster_phC") as c:
            c.attr(
                label="Phase C — New Sections",
                style="dashed",
                color=BORDER["p3"],
                fontname=FONT,
                fontsize="10",
            )
            n(
                c,
                "sec_cr",
                "Section Creator\nrun_create_section()\n→ SectionRevision\n(for gaps with no existing section)",
                FILL["agent"],
                BORDER["p3"],
            )

        with p3.subgraph(name="cluster_phD") as d:
            d.attr(
                label="Phase D — Improvement Roadmap",
                style="dashed",
                color="#4A148C",
                fontname=FONT,
                fontsize="10",
            )
            n(
                d,
                "rd_plan",
                "Roadmap Planner\nrun_roadmap_planner()\n→ ImprovementRoadmap\nImmediate / Short / Medium tiers",
                FILL["agent"],
                BORDER["p3"],
            )
            n(
                d,
                "rd_val",
                "Roadmap Validator\nvalidate_roadmap()\nCODE: ≥90% gap ID coverage\nLLM: coherence + specificity",
                FILL["agent"],
                BORDER["p3"],
            )
            n(
                d,
                "rd_det",
                "Roadmap Detailer\nrun_roadmap_detailer()\n→ ImprovementRoadmap\n(enriched action items)",
                FILL["agent"],
                BORDER["p3"],
            )

        n(
            p3,
            "f_pol",
            "revised_policy.md",
            FILL["file"],
            BORDER["p3"],
            shape="cylinder",
        )
        n(
            p3,
            "f_rmap",
            "revision_report.md\nimprovement_roadmap.md",
            FILL["file"],
            BORDER["p3"],
            shape="cylinder",
        )

    # ════════════════════════════════════════════════════════════════════════
    # EDGES — ordered to avoid crossings
    # ════════════════════════════════════════════════════════════════════════
    P1 = BORDER["p1"]
    P2 = BORDER["p2"]
    P3 = BORDER["p3"]
    IN = BORDER["infra"]
    NK = BORDER["nist"]

    # Title
    e(g, "TITLE", "main", color="#9FA8DA", style="dashed", arr="none")

    # CLI → phases
    e(g, "main", "run_ext", color=P1)
    e(g, "main", "run_ana", color=P2)
    e(g, "main", "run_rev", color=P3)
    e(g, "run_ext", "extractor", color=P1)
    e(g, "run_ana", "gap_ana", color=P2)
    e(g, "run_rev", "pol_rev", color=P3)

    # ── Phase 1 internal ────────────────────────────────────────────────────
    e(g, "extractor", "pdf", label="pdf_path", color=P1)
    e(g, "pdf", "extractor", label="markdown text", color=P1)
    e(g, "extractor", "hdet", label="doc_lines", color=P1)
    e(
        g,
        "hdet",
        "extractor",
        label="HeadingCandidate list\n(fast path: ≥2 found)",
        color=P1,
    )
    e(g, "extractor", "ag1", label="chunk_text\n(sliding window)", color=P1)
    e(g, "ag1", "ag2", label="ExtractionResult", color=P1)
    e(g, "ag2", "ag3", label="ValidationResult\n(if invalid)", color=P1)
    e(g, "ag3", "ag2", label="corrected boundaries", color=P1, style="dashed")
    e(g, "ag1", "ag4", label="ExtractedSection", color=P1)
    e(g, "ag4", "f_mst", label="summaries", color=P1)
    e(g, "extractor", "f_sec", color=P1)
    e(g, "extractor", "f_mst", color=P1)

    # ── Phase 2 internal ────────────────────────────────────────────────────
    e(g, "gap_ana", "fn_cls", label="policy_content", color=P2)
    e(g, "fn_cls", "sub_cls", label="relevant_functions", color=P2)
    e(g, "sub_cls", "map_ph", label="in_scope_ids", color=P2)
    e(g, "map_ph", "red_ph", label="evidence snippets", color=P2)
    e(g, "red_ph", "fn_sum", label="list[SubcategoryAssessment]", color=P2)
    e(g, "fn_sum", "mst_sum", label="FunctionGapSummary × 6", color=P2)
    e(g, "fn_sum", "consol", color=P2)
    e(g, "red_ph", "f_ass", color=P2)
    e(g, "mst_sum", "f_rpts", color=P2)
    e(g, "consol", "f_rpts", color=P2)

    # ── Phase 3 internal ────────────────────────────────────────────────────
    e(g, "pol_rev", "gap_tgt", label="all_assessments + sections", color=P3)
    # Phase A
    e(g, "gap_tgt", "add_w", label="GapTarget (modify)", color=P3)
    e(g, "add_w", "cove_q", label="AdditionBlock", color=P3)
    e(g, "cove_q", "cove_v", label="verification questions", color=P3)
    e(
        g,
        "cove_v",
        "add_w",
        label="retry on failure\n(failed questions as feedback)",
        color=P3,
        style="dashed",
    )
    e(g, "add_w", "clust_s", label="validated AdditionBlocks", color=P3)
    e(
        g,
        "clust_s",
        "add_w",
        label="ClusterSummary\n(RAPTOR prior context)",
        color=P3,
        style="dashed",
    )
    # Phase B
    e(g, "clust_s", "int_ed", label="all blocks + original section", color=P3)
    e(g, "int_ed", "int_val", label="IntegrationResult", color=P3)
    e(g, "int_val", "int_ed", label="retry on failure", color=P3, style="dashed")
    e(g, "int_ed", "f_pol", color=P3)
    # Phase C
    e(g, "gap_tgt", "sec_cr", label="GapTarget (new_section)", color=P3)
    e(g, "sec_cr", "f_pol", color=P3)
    # Phase D
    e(
        g,
        "pol_rev",
        "rd_plan",
        label="assessments\n+ FunctionGapSummary",
        color="#6A1B9A",
    )
    e(g, "rd_plan", "rd_val", color="#6A1B9A")
    e(g, "rd_val", "rd_plan", label="retry on failure", color="#6A1B9A", style="dashed")
    e(g, "rd_val", "rd_det", label="validated ImprovementRoadmap", color="#6A1B9A")
    e(g, "rd_det", "rd_val", label="re-validate", color="#6A1B9A", style="dashed")
    e(g, "rd_det", "f_rmap", color="#6A1B9A")
    e(g, "int_ed", "f_rmap", label="revision_report", color=P3)

    # ── Cross-phase file handoffs ────────────────────────────────────────────
    e(
        g,
        "f_sec",
        "gap_ana",
        label="sections_output.json",
        color="#78909C",
        style="dashed",
    )
    e(g, "f_mst", "gap_ana", label="master_list.json", color="#78909C", style="dashed")
    e(g, "f_ass", "pol_rev", label="assessments.json", color="#78909C", style="dashed")
    e(
        g,
        "f_sec",
        "pol_rev",
        label="sections_output.json",
        color="#78909C",
        style="dashed",
    )

    # ── Infrastructure connections ───────────────────────────────────────────
    e(g, "extractor", "llm", label="create_llm()", color=IN, style="dashed")
    e(g, "gap_ana", "llm", label="create_llm()", color=IN, style="dashed")
    e(g, "pol_rev", "llm", label="create_llm()", color=IN, style="dashed")

    e(
        g,
        "map_ph",
        "txt_sum",
        label="summarize_lossless()\nsection content",
        color=IN,
        style="dashed",
    )
    e(
        g,
        "fn_sum",
        "txt_sum",
        label="summarize_lossless()\nreport text",
        color=IN,
        style="dashed",
    )
    e(
        g,
        "add_w",
        "txt_sum",
        label="summarize_lossless()\nstyle sample / recommendation",
        color=IN,
        style="dashed",
    )
    e(
        g,
        "rd_plan",
        "txt_sum",
        label="summarize_lossless()\ngaps_text",
        color=IN,
        style="dashed",
    )

    e(
        g,
        "llm",
        "txt_sum",
        label="shared singleton",
        color=IN,
        style="dotted",
        arr="none",
    )

    # ── NIST Knowledge Base connections ─────────────────────────────────────
    e(g, "nist_cfg", "gap_tools", color=NK)
    e(g, "framework", "gap_tools", color=NK)
    e(g, "gap_tools", "sub_cls", label="subcategory defs", color=NK, style="dashed")
    e(g, "gap_tools", "red_ph", label="framework excerpt", color=NK, style="dashed")
    e(
        g,
        "gap_tools",
        "gap_tgt",
        label="NIST guidance\n+ framework excerpt",
        color=NK,
        style="dashed",
    )

    return g


if __name__ == "__main__":
    import os

    g = build()
    out = os.path.join(os.path.dirname(__file__), "architecture")
    rendered = g.render(out, cleanup=True)
    print(f"Saved: {rendered}")

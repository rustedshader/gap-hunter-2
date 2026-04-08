import React, { useEffect, useMemo, useState } from "react";
import type { RunRecord } from "../types";
import type { RunData, View } from "../types/ui";
import {
  buildEvidenceMap,
  formatBytes,
  formatDateTime,
  formatDuration,
  parseRevisionReport,
  parseRoadmap,
  summarizeAssessments,
  truncate
} from "../utils/analysis";

const STEP_TITLES = [
  "1. Input policy",
  "2. Extraction output",
  "3. Section analysis",
  "4. Evidence mapping",
  "5. Gap matrix",
  "6. Revision output",
  "7. Artifacts and next steps"
];

type DemoViewProps = {
  demoRun: RunRecord | null;
  onNavigate: (view: View) => void;
  onActivateRun: (runId: string, view: View) => void;
};

export default function DemoView({ demoRun, onNavigate, onActivateRun }: DemoViewProps) {
  const [demoData, setDemoData] = useState<RunData | null>(null);
  const [demoState, setDemoState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [stepIndex, setStepIndex] = useState(0);
  const [autoPlay, setAutoPlay] = useState(false);

  useEffect(() => {
    if (!demoRun) {
      setDemoData(null);
      setDemoState("idle");
      return;
    }

    setStepIndex(0);
    setAutoPlay(false);

    let isActive = true;
    const load = async () => {
      setDemoState("loading");
      try {
        const [
          sectionsRaw,
          masterListRaw,
          assessmentsRaw,
          summaryRaw,
          revisionReportRaw,
          revisedPolicyRaw,
          roadmapRaw
        ] = await Promise.all([
          window.api.readRunJson(demoRun.id, "sections_output.json"),
          window.api.readRunJson(demoRun.id, "master_list.json"),
          window.api.readRunJson(demoRun.id, "assessments.json"),
          window.api.readRunJson(demoRun.id, "summary.json"),
          window.api.readRunText(demoRun.id, "revision_report.md", 800_000),
          window.api.readRunText(demoRun.id, "revised_policy.md", 800_000),
          window.api.readRunText(demoRun.id, "improvement_roadmap.md", 800_000)
        ]);

        if (!isActive) {
          return;
        }

        const sections = Array.isArray(sectionsRaw) ? sectionsRaw : [];
        const masterList = Array.isArray(masterListRaw) ? masterListRaw : [];
        const assessments = (assessmentsRaw || {}) as Record<string, any[]>;
        const summary = (summaryRaw || null) as Record<string, unknown> | null;
        const revisionReport = revisionReportRaw
          ? parseRevisionReport(revisionReportRaw)
          : null;
        const roadmap = roadmapRaw ? parseRoadmap(roadmapRaw) : null;

        setDemoData({
          sections,
          masterList,
          assessments,
          summary,
          revisionReport,
          revisedPolicy: revisedPolicyRaw || null,
          roadmap
        });
        setDemoState("ready");
      } catch (error) {
        if (isActive) {
          setDemoState("error");
        }
      }
    };

    load();
    return () => {
      isActive = false;
    };
  }, [demoRun?.id]);

  useEffect(() => {
    if (!autoPlay) {
      return;
    }
    if (stepIndex >= STEP_TITLES.length - 1) {
      setAutoPlay(false);
      return;
    }
    const timer = window.setTimeout(() => {
      setStepIndex((prev) => Math.min(prev + 1, STEP_TITLES.length - 1));
    }, 2400);
    return () => window.clearTimeout(timer);
  }, [autoPlay, stepIndex]);

  const sections = demoData?.sections || [];
  const assessments = demoData?.assessments || {};
  const allAssessments = useMemo(() => Object.values(assessments).flat(), [assessments]);
  const coverageCounts = useMemo(
    () => summarizeAssessments(allAssessments as any),
    [allAssessments]
  );
  const evidenceMap = useMemo(() => buildEvidenceMap(sections as any, assessments as any), [sections, assessments]);

  const primarySection = sections[0];
  const evidenceSample = primarySection
    ? (evidenceMap[primarySection.number] || []).slice(0, 3)
    : [];
  const gapSample = allAssessments.filter((item: any) => item.status === "Not Addressed").slice(0, 3);
  const revisionBullets = gapSample.length
    ? gapSample.map((item: any) => `${item.subcategory_id}: ${truncate(item.recommendation || item.gap || item.title, 140)}`)
    : ["Sample revision items will appear here once gaps are available."];

  const artifactList = demoRun?.artifacts || [];
  const demoRoadmap = gapSample.map((item: any, index: number) => {
    const label = index === 0 ? "Immediate" : index === 1 ? "Next" : "Later";
    return `${label}: ${truncate(item.title || item.recommendation || item.subcategory_id, 120)}`;
  });

  const steps = useMemo(() => {
    return [
      {
        title: STEP_TITLES[0],
        kicker: "Input policy",
        content: (
          <div className="demo-kv">
            <div>
              <span className="meta-label">Policy</span>
              <strong>{demoRun?.policyName || "Sample policy"}</strong>
            </div>
            <div>
              <span className="meta-label">Run ID</span>
              <strong>{demoRun?.id || "-"}</strong>
            </div>
            <div>
              <span className="meta-label">Created</span>
              <strong>{formatDateTime(demoRun?.createdAt || null)}</strong>
            </div>
            <div>
              <span className="meta-label">Duration</span>
              <strong>{formatDuration(demoRun?.durationMs || null)}</strong>
            </div>
          </div>
        )
      },
      {
        title: STEP_TITLES[1],
        kicker: "Extraction",
        content: (
          <div className="demo-list">
            <div className="demo-pill">Sections extracted: {sections.length}</div>
            <div className="demo-sublist">
              {sections.slice(0, 4).map((section: any) => (
                <div key={section.number} className="demo-subitem">
                  <strong>{section.number}. {section.title}</strong>
                  <span>{truncate(section.summary || section.content || "", 120)}</span>
                </div>
              ))}
            </div>
          </div>
        )
      },
      {
        title: STEP_TITLES[2],
        kicker: "Section analysis",
        content: primarySection ? (
          <div className="demo-panel">
            <div className="pill">Section {primarySection.number}</div>
            <h3>{primarySection.title}</h3>
            <p>{truncate(primarySection.content || "", 420)}</p>
          </div>
        ) : (
          <div className="empty">No sections available in the demo data.</div>
        )
      },
      {
        title: STEP_TITLES[3],
        kicker: "Evidence mapping",
        content: evidenceSample.length ? (
          <div className="demo-sublist">
            {evidenceSample.map((item: any) => (
              <div key={item.subcategory_id} className="demo-subitem">
                <strong>{item.subcategory_id} - {item.status}</strong>
                <span>{truncate(item.evidence || "", 160)}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty">No evidence mapped for the first section.</div>
        )
      },
      {
        title: STEP_TITLES[4],
        kicker: "Gap matrix",
        content: (
          <div className="demo-metrics">
            <div className="stat">
              <span>Total</span>
              <strong>{coverageCounts.total}</strong>
            </div>
            <div className="stat">
              <span>Addressed</span>
              <strong>{coverageCounts.addressed}</strong>
            </div>
            <div className="stat">
              <span>Partial</span>
              <strong>{coverageCounts.partiallyAddressed}</strong>
            </div>
            <div className="stat">
              <span>Gaps</span>
              <strong>{coverageCounts.notAddressed}</strong>
            </div>
          </div>
        )
      },
      {
        title: STEP_TITLES[5],
        kicker: "Revision output",
        content: (
          <div className="demo-panel">
            <div className="demo-pill">Demo summary (no LLM calls)</div>
            <ul>
              {revisionBullets.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        )
      },
      {
        title: STEP_TITLES[6],
        kicker: "Artifacts and next steps",
        content: (
          <div className="demo-grid">
            <div className="demo-panel">
              <div className="demo-pill">Artifacts</div>
              {artifactList.length === 0 ? (
                <div className="empty">No artifacts listed yet.</div>
              ) : (
                <div className="demo-sublist">
                  {artifactList.slice(0, 6).map((item) => (
                    <div key={item.path} className="demo-subitem">
                      <strong>{item.name}</strong>
                      <span>{formatBytes(item.size || 0)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="demo-panel">
              <div className="demo-pill">Roadmap snapshot</div>
              {demoRoadmap.length ? (
                <ul>
                  {demoRoadmap.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              ) : (
                <div className="empty">No roadmap items available.</div>
              )}
            </div>
          </div>
        )
      }
    ];
  }, [
    demoRun,
    sections,
    primarySection,
    evidenceSample,
    coverageCounts,
    revisionBullets,
    artifactList,
    demoRoadmap
  ]);

  const activeStep = steps[stepIndex];

  if (!demoRun) {
    return (
      <section className="card">
        <div className="card-header">
          <div>
            <h2>Guided demo</h2>
            <span className="subtle">No demo data available</span>
          </div>
        </div>
        <div className="empty">
          Demo data was not found. Add a sample run under app/resources/demo-run or
          generate a local run to enable the guided demo.
        </div>
      </section>
    );
  }

  return (
    <div className="stack">
      <section className="card demo-hero">
        <div className="card-header">
          <div>
            <h2>Guided Demo</h2>
            <span className="subtle">Offline walkthrough using precomputed data</span>
          </div>
          <div className="demo-badge">Demo mode</div>
        </div>
        <p className="demo-lead">
          This walkthrough replays a stored run to show the full workflow. No backend
          execution or LLM calls are triggered.
        </p>
        <div className="demo-actions">
          <button
            className="ghost"
            onClick={() => onActivateRun(demoRun.id, "dashboard")}
          >
            Open demo run in dashboard
          </button>
          <button className="ghost" onClick={() => onNavigate("library")}>See run library</button>
          <button
            className="ghost"
            onClick={() => demoRun.runDir && window.api.openPath(demoRun.runDir)}
            disabled={!demoRun.runDir}
          >
            Open demo folder
          </button>
        </div>
      </section>

      <div className="demo-layout">
        <section className="card demo-steps">
          <div className="card-header">
            <div>
              <h2>Workflow steps</h2>
              <span className="subtle">Click a step to focus</span>
            </div>
          </div>
          <div className="demo-stepper">
            {STEP_TITLES.map((title, index) => (
              <button
                key={title}
                className={`demo-step ${index === stepIndex ? "active" : ""}`}
                onClick={() => setStepIndex(index)}
              >
                <span className="step-index">{index + 1}</span>
                <span>{title}</span>
              </button>
            ))}
          </div>
          <div className="demo-controls">
            <button
              className="ghost"
              onClick={() => setStepIndex((prev) => Math.max(prev - 1, 0))}
              disabled={stepIndex === 0}
            >
              Back
            </button>
            <button
              className="primary"
              onClick={() => setStepIndex((prev) => Math.min(prev + 1, steps.length - 1))}
              disabled={stepIndex === steps.length - 1}
            >
              Next
            </button>
            <button className="ghost" onClick={() => setAutoPlay((prev) => !prev)}>
              {autoPlay ? "Pause" : "Auto-play"}
            </button>
          </div>
        </section>

        <section className="card demo-stage">
          <div className="card-header">
            <div>
              <h2>{activeStep.title}</h2>
              <span className="subtle">{activeStep.kicker}</span>
            </div>
            <span className={`demo-state ${demoState}`}>{demoState}</span>
          </div>
          {demoState === "loading" && <div className="empty">Loading demo data...</div>}
          {demoState === "error" && (
            <div className="empty">Demo data could not be loaded.</div>
          )}
          {demoState === "ready" && <div className="demo-content">{activeStep.content}</div>}
        </section>
      </div>
    </div>
  );
}

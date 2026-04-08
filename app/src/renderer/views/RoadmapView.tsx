import React from "react";
import SegmentedTabs from "../components/SegmentedTabs";
import type { RoadmapView as RoadmapViewKind, RunData } from "../types/ui";

type RoadmapCounts = { tiers: number; items: number; missing: number };

type RoadmapViewProps = {
  roadmapView: RoadmapViewKind;
  onSetRoadmapView: (view: RoadmapViewKind) => void;
  runData: RunData | null;
  roadmapCounts: RoadmapCounts;
  runDir: string;
};

export default function RoadmapView({
  roadmapView,
  onSetRoadmapView,
  runData,
  roadmapCounts,
  runDir
}: RoadmapViewProps) {
  return (
    <div className="stack">
      <div className="page-tabs">
        <SegmentedTabs
          value={roadmapView}
          onChange={onSetRoadmapView}
          options={[
            { value: "overview", label: "Overview" },
            { value: "tiers", label: "Priority tiers" },
            { value: "missing", label: "Missing docs" }
          ]}
        />
      </div>

      {roadmapView === "overview" && (
        <div className="grid">
          <section className="card span-12">
            <div className="card-header">
              <div>
                <h2>Roadmap overview</h2>
                <span className="subtle">Priority execution plan</span>
              </div>
            </div>
            {runData?.roadmap ? (
              <>
                <p>{runData.roadmap.executiveSummary}</p>
                <div className="stat-grid compact">
                  <div className="stat">
                    <span>Tiers</span>
                    <strong>{roadmapCounts.tiers}</strong>
                  </div>
                  <div className="stat">
                    <span>Initiatives</span>
                    <strong>{roadmapCounts.items}</strong>
                  </div>
                  <div className="stat">
                    <span>Missing docs</span>
                    <strong>{roadmapCounts.missing}</strong>
                  </div>
                  <div className="stat">
                    <span>Run dir</span>
                    <strong>{runDir || "-"}</strong>
                  </div>
                </div>
              </>
            ) : (
              <div className="empty">No roadmap available for this run.</div>
            )}
          </section>
        </div>
      )}

      {roadmapView === "tiers" && (
        <div className="grid">
          {(runData?.roadmap?.tiers || []).map((tier) => (
            <section key={tier.tierName} className="card span-6">
              <div className="card-header">
                <div>
                  <h2>{tier.tierName}</h2>
                  <span className="subtle">{tier.rationale}</span>
                </div>
              </div>
              <div className="roadmap-list">
                {tier.items.map((item) => (
                  <div key={item.title} className="roadmap-item">
                    <strong>{item.title}</strong>
                    <span>NIST: {item.nistReference || "-"}</span>
                    <p>{item.description}</p>
                    <div className="roadmap-meta">
                      <span>Owner: {item.responsible}</span>
                      <span>Effort: {item.effort}</span>
                    </div>
                    <div className="note">Success: {item.successCriteria}</div>
                    <div className="note">Dependencies: {item.dependencies}</div>
                  </div>
                ))}
              </div>
            </section>
          ))}
        </div>
      )}

      {roadmapView === "missing" && (
        <div className="grid">
          <section className="card span-12">
            <div className="card-header">
              <div>
                <h2>Missing policy documents</h2>
                <span className="subtle">Templates to produce</span>
              </div>
            </div>
            {runData?.roadmap?.missingDocs.length ? (
              <ul className="doc-list">
                {runData.roadmap.missingDocs.map((doc) => (
                  <li key={doc}>{doc}</li>
                ))}
              </ul>
            ) : (
              <div className="empty">No missing document list found.</div>
            )}
          </section>
        </div>
      )}
    </div>
  );
}

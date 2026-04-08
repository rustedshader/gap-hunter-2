import React from "react";
import SegmentedTabs from "../components/SegmentedTabs";
import type { RevisionView as RevisionViewKind, RunData } from "../types/ui";
import { buildOriginalPolicy } from "../utils/analysis";

type RevisionViewProps = {
  revisionView: RevisionViewKind;
  onSetRevisionView: (view: RevisionViewKind) => void;
  runData: RunData | null;
};

export default function RevisionView({
  revisionView,
  onSetRevisionView,
  runData
}: RevisionViewProps) {
  return (
    <div className="stack">
      <div className="page-tabs">
        <SegmentedTabs
          value={revisionView}
          onChange={onSetRevisionView}
          options={[
            { value: "summary", label: "Summary" },
            { value: "compare", label: "Compare" },
            { value: "final", label: "Final policy" }
          ]}
        />
      </div>

      {revisionView === "summary" && (
        <div className="grid">
          <section className="card span-12">
            <div className="card-header">
              <div>
                <h2>Revision report</h2>
                <span className="subtle">Change rationale and coverage</span>
              </div>
            </div>
            {runData?.revisionReport ? (
              <div className="stat-grid">
                <div className="stat">
                  <span>Gaps addressed</span>
                  <strong>{runData.revisionReport.totalGaps}</strong>
                </div>
                <div className="stat">
                  <span>Sections modified</span>
                  <strong>{runData.revisionReport.modifiedSections}</strong>
                </div>
                <div className="stat">
                  <span>New sections</span>
                  <strong>{runData.revisionReport.newSections}</strong>
                </div>
                <div className="stat">
                  <span>Changes</span>
                  <strong>{runData.revisionReport.changes.length}</strong>
                </div>
              </div>
            ) : (
              <div className="empty">No revision report found.</div>
            )}
          </section>

          <section className="card span-12">
            <div className="card-header">
              <div>
                <h2>Change rationale</h2>
                <span className="subtle">Revision report details</span>
              </div>
            </div>
            {runData?.revisionReport?.changes.length ? (
              <div className="change-grid">
                {runData.revisionReport.changes.map((change) => (
                  <div key={change.id} className="change-card">
                    <div className="pill">{change.id}</div>
                    <strong>{change.action}</strong>
                    <span>{change.section}</span>
                    <p>{change.description}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty">No change entries available.</div>
            )}
          </section>
        </div>
      )}

      {revisionView === "compare" && (
        <div className="grid">
          <section className="card span-6">
            <div className="card-header">
              <div>
                <h2>Original policy</h2>
                <span className="subtle">Extracted content</span>
              </div>
            </div>
            <div className="policy-panel">
              <pre>{buildOriginalPolicy(runData?.sections || [])}</pre>
            </div>
          </section>

          <section className="card span-6">
            <div className="card-header">
              <div>
                <h2>Revised policy</h2>
                <span className="subtle">Generated output</span>
              </div>
            </div>
            <div className="policy-panel">
              <pre>{runData?.revisedPolicy || "No revised policy found."}</pre>
            </div>
          </section>
        </div>
      )}

      {revisionView === "final" && (
        <div className="grid">
          <section className="card span-12">
            <div className="card-header">
              <div>
                <h2>Final revised policy</h2>
                <span className="subtle">Ready for export</span>
              </div>
            </div>
            <div className="policy-panel">
              <pre>{runData?.revisedPolicy || "No revised policy found."}</pre>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}

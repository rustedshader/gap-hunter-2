import React from "react";
import SegmentedTabs from "../components/SegmentedTabs";
import { NIST_FUNCTIONS } from "../constants";
import type {
  MatrixView as MatrixViewKind,
  StatusCounts,
  SubcategoryAssessment
} from "../types/ui";
import { getFunctionSummary, statusClass } from "../utils/analysis";

type MatrixViewProps = {
  matrixView: MatrixViewKind;
  onSetMatrixView: (view: MatrixViewKind) => void;
  matrixSummary: Record<string, StatusCounts>;
  matrixFunction: string;
  onSetMatrixFunction: (name: string) => void;
  matrixAssessments: SubcategoryAssessment[];
  selectedAssessment: SubcategoryAssessment | null;
  onSelectAssessment: (assessment: SubcategoryAssessment | null) => void;
  assessments: Record<string, SubcategoryAssessment[]> | null;
};

export default function MatrixView({
  matrixView,
  onSetMatrixView,
  matrixSummary,
  matrixFunction,
  onSetMatrixFunction,
  matrixAssessments,
  selectedAssessment,
  onSelectAssessment,
  assessments
}: MatrixViewProps) {
  return (
    <div className="stack">
      <div className="page-tabs">
        <SegmentedTabs
          value={matrixView}
          onChange={onSetMatrixView}
          options={[
            { value: "overview", label: "Overview" },
            { value: "matrix", label: "Subcategory matrix" }
          ]}
        />
        <div className="badge-row">
          <span className="badge success">Addressed</span>
          <span className="badge warning">Partial</span>
          <span className="badge danger">Gaps</span>
          <span className="badge muted">Out of scope</span>
        </div>
      </div>

      {matrixView === "overview" && (
        <div className="grid">
          <section className="card span-12">
            <div className="card-header">
              <div>
                <h2>Function coverage</h2>
                <span className="subtle">At-a-glance posture by NIST function</span>
              </div>
            </div>
            <div className="function-grid">
              {NIST_FUNCTIONS.map((name) => {
                const summary = matrixSummary[name];
                return (
                  <button
                    key={name}
                    className={`function-card ${matrixFunction === name ? "active" : ""}`}
                    onClick={() => {
                      onSetMatrixFunction(name);
                      onSetMatrixView("matrix");
                    }}
                  >
                    <div className="function-header">
                      <strong>{name}</strong>
                      <span className="meta-label">{summary.total} subcategories</span>
                    </div>
                    <div className="badge-row">
                      <span className="badge success">{summary.addressed} addressed</span>
                      <span className="badge warning">
                        {summary.partiallyAddressed} partial
                      </span>
                      <span className="badge danger">{summary.notAddressed} gaps</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </section>
        </div>
      )}

      {matrixView === "matrix" && (
        <div className="grid">
          <section className="card span-4">
            <div className="card-header">
              <div>
                <h2>Functions</h2>
                <span className="subtle">Coverage by function</span>
              </div>
            </div>
            <div className="list">
              {NIST_FUNCTIONS.map((name) => (
                <button
                  key={name}
                  className={`list-item ${matrixFunction === name ? "active" : ""}`}
                  onClick={() => onSetMatrixFunction(name)}
                >
                  <span>{name}</span>
                  <strong>{getFunctionSummary(assessments || {}, name)}</strong>
                </button>
              ))}
            </div>
          </section>

          <section className="card span-8">
            <div className="card-header">
              <div>
                <h2>{matrixFunction} Coverage</h2>
                <span className="subtle">Subcategory matrix</span>
              </div>
            </div>
            {matrixAssessments.length === 0 ? (
              <div className="empty">No assessments loaded yet.</div>
            ) : (
              <div className="matrix-grid">
                {matrixAssessments.map((assessment) => (
                  <button
                    key={assessment.subcategory_id}
                    className={`matrix-chip ${statusClass(assessment.status)}`}
                    onClick={() => onSelectAssessment(assessment)}
                  >
                    <span>{assessment.subcategory_id}</span>
                    <small>{assessment.status}</small>
                  </button>
                ))}
              </div>
            )}
            {selectedAssessment && (
              <div className="detail-card">
                <div className="pill">{selectedAssessment.subcategory_id}</div>
                <h3>{selectedAssessment.title}</h3>
                <p>
                  <strong>Status:</strong> {selectedAssessment.status}
                </p>
                <p>
                  <strong>Evidence:</strong> {selectedAssessment.evidence}
                </p>
                <p>
                  <strong>Gap:</strong> {selectedAssessment.gap}
                </p>
                <p>
                  <strong>Recommendation:</strong> {selectedAssessment.recommendation}
                </p>
              </div>
            )}
          </section>
        </div>
      )}
    </div>
  );
}

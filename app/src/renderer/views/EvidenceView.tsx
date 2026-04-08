import React from "react";
import type {
  AssessmentStatus,
  PolicySection,
  StatusCounts,
  SubcategoryAssessment
} from "../types/ui";
import {
  getSectionContent,
  getSectionTitle,
  statusClass,
  truncate
} from "../utils/analysis";

type EvidenceViewProps = {
  sections: PolicySection[];
  filteredSections: PolicySection[];
  selectedSection: string | null;
  onSelectSection: (section: string) => void;
  sectionSearch: string;
  onSectionSearchChange: (value: string) => void;
  evidenceCounts: StatusCounts;
  evidenceStatus: AssessmentStatus | "All";
  onEvidenceStatusChange: (status: AssessmentStatus | "All") => void;
  evidenceForSection: SubcategoryAssessment[];
};

export default function EvidenceView({
  sections,
  filteredSections,
  selectedSection,
  onSelectSection,
  sectionSearch,
  onSectionSearchChange,
  evidenceCounts,
  evidenceStatus,
  onEvidenceStatusChange,
  evidenceForSection
}: EvidenceViewProps) {
  const hasSections = sections.length > 0;
  const showNoMatches = hasSections && filteredSections.length === 0;
  const evidenceEmptyMessage = selectedSection
    ? "No evidence mapped to this section."
    : "Select a section to see evidence.";

  return (
    <div className="grid grid-top evidence-grid">
      <section className="card span-4">
        <div className="card-header">
          <div>
            <h2>Section browser</h2>
            <span className="subtle">Policy structure</span>
          </div>
        </div>
        <div className="field-group">
          <label>Search sections</label>
          <input
            type="text"
            placeholder="Search by section number or title"
            value={sectionSearch}
            onChange={(event) => onSectionSearchChange(event.target.value)}
          />
        </div>
        <div className="list">
          {!hasSections ? (
            <div className="empty">No sections loaded yet.</div>
          ) : showNoMatches ? (
            <div className="empty">No sections match this search.</div>
          ) : (
            filteredSections.map((section) => (
              <button
                key={section.number}
                className={`list-item ${selectedSection === section.number ? "active" : ""}`}
                onClick={() => onSelectSection(section.number)}
              >
                <span>{section.number}</span>
                <strong>{section.title}</strong>
              </button>
            ))
          )}
        </div>
      </section>

      <div className="span-8 stack">
        <section className="card">
          <div className="card-header">
            <div>
              <h2>Section detail</h2>
              <span className="subtle">Original policy text</span>
            </div>
          </div>
          <div className="scroll-pane">
            {selectedSection ? (
              <div className="text-block">
                <h3>Section {selectedSection}</h3>
                <p className="meta-label">
                  {getSectionTitle(sections, selectedSection)}
                </p>
                <p>{getSectionContent(sections, selectedSection) || "No content available."}</p>
              </div>
            ) : (
              <div className="empty">Select a section to view details.</div>
            )}
          </div>
        </section>

        <section className="card">
          <div className="card-header">
            <div>
              <h2>Evidence matches</h2>
              <span className="subtle">Mapped subcategories</span>
            </div>
          </div>
          <div className="stat-grid compact">
            <div className="stat">
              <span>Addressed</span>
              <strong>{evidenceCounts.addressed}</strong>
            </div>
            <div className="stat">
              <span>Partial</span>
              <strong>{evidenceCounts.partiallyAddressed}</strong>
            </div>
            <div className="stat">
              <span>Gaps</span>
              <strong>{evidenceCounts.notAddressed}</strong>
            </div>
            <div className="stat">
              <span>Out of scope</span>
              <strong>{evidenceCounts.outOfScope}</strong>
            </div>
          </div>
          <div className="field-group">
            <label>Status filter</label>
            <select
              value={evidenceStatus}
              onChange={(event) =>
                onEvidenceStatusChange(event.target.value as AssessmentStatus | "All")
              }
            >
              <option value="All">All</option>
              <option value="Addressed">Addressed</option>
              <option value="Partially Addressed">Partially Addressed</option>
              <option value="Not Addressed">Not Addressed</option>
              <option value="Out of Scope">Out of Scope</option>
            </select>
          </div>
          <div className="list">
            {evidenceForSection.length === 0 ? (
              <div className="empty">{evidenceEmptyMessage}</div>
            ) : (
              evidenceForSection.map((item) => (
                <div key={item.subcategory_id} className={`evidence-card ${statusClass(item.status)}`}>
                  <div className="pill">{item.subcategory_id}</div>
                  <strong>{item.title}</strong>
                  <span>{item.status}</span>
                  <p>{truncate(item.evidence, 160)}</p>
                </div>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

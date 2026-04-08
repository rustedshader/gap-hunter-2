import React from "react";
import RunDetails from "../components/RunDetails";
import type { RunRecord } from "../types";
import { formatDateTime, formatDuration } from "../utils/analysis";

type LibraryViewProps = {
  runLibraryFiltered: RunRecord[];
  librarySearch: string;
  libraryStatus: string;
  libraryType: string;
  libraryProvider: string;
  librarySort: string;
  libraryPinnedOnly: boolean;
  libraryDateFrom: string;
  libraryDateTo: string;
  statusOptions: string[];
  providerOptions: string[];
  onLibrarySearchChange: (value: string) => void;
  onLibraryStatusChange: (value: string) => void;
  onLibraryTypeChange: (value: string) => void;
  onLibraryProviderChange: (value: string) => void;
  onLibrarySortChange: (value: string) => void;
  onLibraryPinnedOnlyChange: (value: boolean) => void;
  onLibraryDateFromChange: (value: string) => void;
  onLibraryDateToChange: (value: string) => void;
  selectedRunId: string | null;
  runHistory: RunRecord[];
  onSelectRun: (entry: RunRecord) => void;
  onScanRuns: () => void;
  onUpdateHistoryEntry: (entry: RunRecord, updates: Partial<RunRecord>) => void;
  onOpenRunDir: () => void;
  onRemoveRun: (entry: RunRecord, options: { deleteFiles: boolean }) => void;
  onOpenRun: (entry: RunRecord) => void;
};

export default function LibraryView({
  runLibraryFiltered,
  librarySearch,
  libraryStatus,
  libraryType,
  libraryProvider,
  librarySort,
  libraryPinnedOnly,
  libraryDateFrom,
  libraryDateTo,
  statusOptions,
  providerOptions,
  onLibrarySearchChange,
  onLibraryStatusChange,
  onLibraryTypeChange,
  onLibraryProviderChange,
  onLibrarySortChange,
  onLibraryPinnedOnlyChange,
  onLibraryDateFromChange,
  onLibraryDateToChange,
  selectedRunId,
  runHistory,
  onSelectRun,
  onScanRuns,
  onUpdateHistoryEntry,
  onOpenRunDir,
  onRemoveRun,
  onOpenRun
}: LibraryViewProps) {
  const selectedEntry = runHistory.find((item) => item.id === selectedRunId) || null;

  const renderStatusBadge = (status?: string | null) => {
    const value = status || "unknown";
    if (["failed"].includes(value)) {
      return "danger";
    }
    if (["cancelled", "stopping", "force-stopping", "orphaned", "recovering"].includes(value)) {
      return "warning";
    }
    if (["running", "starting", "queued"].includes(value)) {
      return "info";
    }
    if (value === "completed") {
      return "success";
    }
    return "muted";
  };

  return (
    <div className="grid">
      <section className="card span-5">
        <div className="card-header">
          <div>
            <h2>Run library</h2>
            <span className="subtle">Saved runs and tags</span>
          </div>
          <button className="ghost" onClick={onScanRuns}>
            Scan output dir
          </button>
        </div>
        <div className="library-controls">
          <input
            type="text"
            placeholder="Search runs"
            value={librarySearch}
            onChange={(event) => onLibrarySearchChange(event.target.value)}
          />
          <select
            value={libraryStatus}
            onChange={(event) => onLibraryStatusChange(event.target.value)}
          >
            <option value="all">All statuses</option>
            {statusOptions.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
          <select value={libraryType} onChange={(event) => onLibraryTypeChange(event.target.value)}>
            <option value="all">All types</option>
            <option value="real">Real runs</option>
            <option value="demo">Demo runs</option>
          </select>
          <select value={librarySort} onChange={(event) => onLibrarySortChange(event.target.value)}>
            <option value="newest">Newest first</option>
            <option value="oldest">Oldest first</option>
            <option value="status">Status</option>
            <option value="name">Name</option>
            <option value="duration">Duration</option>
          </select>
        </div>
        <div className="library-subcontrols">
          <select
            value={libraryProvider}
            onChange={(event) => onLibraryProviderChange(event.target.value)}
          >
            <option value="all">All providers</option>
            {providerOptions.map((provider) => (
              <option key={provider} value={provider}>
                {provider}
              </option>
            ))}
          </select>
          <input
            type="date"
            value={libraryDateFrom}
            onChange={(event) => onLibraryDateFromChange(event.target.value)}
          />
          <input
            type="date"
            value={libraryDateTo}
            onChange={(event) => onLibraryDateToChange(event.target.value)}
          />
          <label className="toggle compact">
            <input
              type="checkbox"
              checked={libraryPinnedOnly}
              onChange={(event) => onLibraryPinnedOnlyChange(event.target.checked)}
            />
            <span>Pinned only</span>
          </label>
        </div>
        <div className="list">
          {runLibraryFiltered.length === 0 ? (
            <div className="empty">No runs match this filter set.</div>
          ) : (
            runLibraryFiltered.map((entry) => (
              <button
                key={entry.id}
                className={`list-item run-item ${entry.id === selectedRunId ? "active" : ""}`}
                onClick={() => onSelectRun(entry)}
              >
                <div className="run-item-header">
                  <div className="run-item-title">
                    <strong>{entry.runName || entry.policyName || "Policy"}</strong>
                    <span className="meta-label">
                      {entry.runName ? entry.policyName || "" : entry.id}
                    </span>
                  </div>
                  <div className="run-badge-row">
                    {entry.pinned && <span className="badge muted">Pinned</span>}
                    {entry.runType === "demo" && <span className="badge muted">Demo</span>}
                    {entry.runDirExists === false && (
                      <span className="badge warning">Missing files</span>
                    )}
                    <span className={`badge ${renderStatusBadge(entry.status)}`}>
                      {entry.status || "unknown"}
                    </span>
                  </div>
                </div>
                <div className="run-item-meta">
                  <span>Created: {formatDateTime(entry.createdAt)}</span>
                  <span>Duration: {formatDuration(entry.durationMs || null)}</span>
                  <span>Sections: {entry.sectionCount ?? "-"}</span>
                  <span>Gaps: {entry.gapCount ?? "-"}</span>
                </div>
              </button>
            ))
          )}
        </div>
      </section>

      <section className="card span-7">
        <div className="card-header">
          <div>
            <h2>Run details</h2>
            <span className="subtle">Tags and notes</span>
          </div>
        </div>
        {selectedRunId ? (
          <RunDetails
            entry={selectedEntry}
            onUpdate={onUpdateHistoryEntry}
            onOpen={onOpenRunDir}
            onRemove={onRemoveRun}
            onOpenRun={onOpenRun}
          />
        ) : (
          <div className="empty">Select a run to view details.</div>
        )}
      </section>
    </div>
  );
}

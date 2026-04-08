import React, { useEffect, useMemo, useState } from "react";
import type { RunRecord } from "../types";
import { formatBytes, formatDateTime, formatDuration } from "../utils/analysis";

type RunDetailsProps = {
  entry: RunRecord | null;
  onUpdate: (entry: RunRecord, updates: Partial<RunRecord>) => void;
  onOpen: () => void;
  onRemove: (entry: RunRecord, options: { deleteFiles: boolean }) => void;
  onOpenRun: (entry: RunRecord) => void;
};

export default function RunDetails({
  entry,
  onUpdate,
  onOpen,
  onRemove,
  onOpenRun
}: RunDetailsProps) {
  const [tags, setTags] = useState("");
  const [notes, setNotes] = useState("");
  const [runName, setRunName] = useState("");
  const [pinned, setPinned] = useState(false);

  useEffect(() => {
    if (!entry) {
      setTags("");
      setNotes("");
      setRunName("");
      setPinned(false);
      return;
    }
    setTags((entry.tags || []).join(", "));
    setNotes(entry.notes || "");
    setRunName(entry.runName || "");
    setPinned(Boolean(entry.pinned));
  }, [entry]);

  if (!entry) {
    return <div className="empty">Select a run to view details.</div>;
  }

  const handleSave = () => {
    const tagList = tags
      .split(",")
      .map((tag) => tag.trim())
      .filter(Boolean);
    onUpdate(entry, { tags: tagList, notes, runName: runName.trim(), pinned });
  };

  const isDemo = entry.runType === "demo";
  const durationLabel = formatDuration(entry.durationMs || null);
  const createdLabel = formatDateTime(entry.createdAt);
  const finishedLabel = formatDateTime(entry.finishedAt || null);
  const missingArtifacts = entry.missingArtifacts || [];
  const artifactBytes = Number.isFinite(entry.artifactTotalBytes)
    ? formatBytes(entry.artifactTotalBytes || 0)
    : "-";
  const executionMode = entry.executionMode || "Full run";
  const statusLabel = entry.status || "-";
  const runDirMissing = entry.runDirExists === false;
  const runTypeLabel = entry.runType === "demo" ? "Demo" : "Real";
  const canOpenFolder = !runDirMissing && Boolean(entry.runDir);

  const counts = useMemo(() => {
    return [
      { label: "Sections", value: entry.sectionCount ?? "-" },
      { label: "Assessments", value: entry.assessmentCount ?? "-" },
      { label: "Gaps", value: entry.gapCount ?? "-" },
      { label: "Artifacts", value: entry.artifactsCount ?? entry.artifacts?.length ?? "-" }
    ];
  }, [entry]);

  return (
    <div className="detail-block">
      <div className={`note${runDirMissing ? " warning" : ""}`}>
        Run directory: {entry.runDir || "-"}
      </div>
      {runDirMissing && (
        <div className="alert warning">Run folder is missing. Some artifacts may be unavailable.</div>
      )}

      <div className="detail-grid">
        <div>
          <span className="meta-label">Display name</span>
          <input
            type="text"
            value={runName}
            onChange={(event) => setRunName(event.target.value)}
            placeholder="Optional title"
            disabled={isDemo}
          />
        </div>
        <div>
          <span className="meta-label">Run type</span>
          <strong>{runTypeLabel}</strong>
        </div>
        <div>
          <span className="meta-label">Policy</span>
          <strong>{entry.policyName || "-"}</strong>
        </div>
        <div>
          <span className="meta-label">Run ID</span>
          <strong>{entry.id}</strong>
        </div>
        <div>
          <span className="meta-label">Source PDF</span>
          <strong>{entry.pdfPath || "-"}</strong>
        </div>
        <div>
          <span className="meta-label">Status</span>
          <strong>{statusLabel}</strong>
        </div>
        <div>
          <span className="meta-label">Execution mode</span>
          <strong>{executionMode}</strong>
        </div>
        <div>
          <span className="meta-label">Output dir</span>
          <strong>{entry.outputDir || "-"}</strong>
        </div>
        <div>
          <span className="meta-label">Provider</span>
          <strong>{entry.provider || "-"}</strong>
        </div>
        <div>
          <span className="meta-label">Model</span>
          <strong>{entry.model || "-"}</strong>
        </div>
        <div>
          <span className="meta-label">Created</span>
          <strong>{createdLabel}</strong>
        </div>
        <div>
          <span className="meta-label">Finished</span>
          <strong>{finishedLabel}</strong>
        </div>
        <div>
          <span className="meta-label">Duration</span>
          <strong>{durationLabel}</strong>
        </div>
        <div>
          <span className="meta-label">Artifacts size</span>
          <strong>{artifactBytes}</strong>
        </div>
      </div>

      <div className="stat-grid compact">
        {counts.map((item) => (
          <div key={item.label} className="stat">
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </div>
        ))}
      </div>

      {missingArtifacts.length > 0 && (
        <div className="missing-block">
          <span className="meta-label">Missing artifacts</span>
          <div className="chip-row">
            {missingArtifacts.map((name) => (
              <span key={name} className="chip warning">
                {name}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="field-group">
        <label>Tags</label>
        <input
          type="text"
          value={tags}
          onChange={(event) => setTags(event.target.value)}
          placeholder="e.g. priority, audit"
          disabled={isDemo}
        />
      </div>

      <div className="field-group">
        <label>Notes</label>
        <textarea
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          rows={6}
          disabled={isDemo}
        />
      </div>

      <label className="toggle">
        <input
          type="checkbox"
          checked={pinned}
          onChange={(event) => setPinned(event.target.checked)}
          disabled={isDemo}
        />
        <span>Pin this run</span>
      </label>

      <div className="actions">
        <button className="primary" onClick={handleSave}>
          Save notes
        </button>
        <button className="ghost" onClick={() => onOpenRun(entry)}>
          Open run
        </button>
        <button className="ghost" onClick={onOpen} disabled={!canOpenFolder}>
          Open folder
        </button>
        {!isDemo && (
          <button
            className="danger"
            onClick={() => {
              if (window.confirm("Remove this run from the library?")) {
                onRemove(entry, { deleteFiles: false });
              }
            }}
          >
            Remove from library
          </button>
        )}
        {!isDemo && (
          <button
            className="danger"
            onClick={() => {
              if (window.confirm("Delete the run folder and remove it from the library?")) {
                onRemove(entry, { deleteFiles: true });
              }
            }}
          >
            Delete run files
          </button>
        )}
      </div>
    </div>
  );
}

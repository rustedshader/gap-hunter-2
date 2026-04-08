import React, { useMemo } from "react";
import type { ExitEvent, StatusEvent } from "../types";
import type { AppConfig, Phase, RunStep } from "../types/ui";
import { RUN_STEP_ORDER, RUN_STEPS } from "../constants";

type RunBuilderViewProps = {
  config: AppConfig;
  runStep: RunStep;
  onSetRunStep: (step: RunStep) => void;
  policyFileName: string;
  validation: string[];
  runStateLabel: string;
  statusEvent: StatusEvent | null;
  exitInfo: ExitEvent | null;
  progressPct: number;
  phases: Phase[];
  logsCount: number;
  onUpdateConfig: (key: keyof AppConfig, value: AppConfig[keyof AppConfig]) => void;
  onSelectPdf: () => void;
  onSelectOutputDir: () => void;
  onSelectRunDir: () => void;
  onViewLogs: () => void;
  onViewArtifacts: () => void;
};

export default function RunBuilderView({
  config,
  runStep,
  onSetRunStep,
  policyFileName,
  validation,
  runStateLabel,
  statusEvent,
  exitInfo,
  progressPct,
  phases,
  logsCount,
  onUpdateConfig,
  onSelectPdf,
  onSelectOutputDir,
  onSelectRunDir,
  onViewLogs,
  onViewArtifacts
}: RunBuilderViewProps) {
  const runStepIndex = RUN_STEP_ORDER.indexOf(runStep);
  const prevRunStep = runStepIndex > 0 ? RUN_STEP_ORDER[runStepIndex - 1] : null;
  const nextRunStep =
    runStepIndex < RUN_STEP_ORDER.length - 1
      ? RUN_STEP_ORDER[runStepIndex + 1]
      : null;

  const activeFlags = useMemo(() => {
    const flags: string[] = [];
    if (config.extractOnly) {
      flags.push("Extract only");
    }
    if (config.skipExtraction) {
      flags.push("Skip extraction");
    }
    if (config.skipRevision) {
      flags.push("Skip revision");
    }
    if (config.revisionOnly) {
      flags.push("Revision only");
    }
    return flags;
  }, [config.extractOnly, config.skipExtraction, config.skipRevision, config.revisionOnly]);

  return (
    <div className="stack">
      <div className="stepper">
        {RUN_STEPS.map((step, index) => {
          const isActive = runStep === step.id;
          const isComplete = runStepIndex > index;
          return (
            <button
              key={step.id}
              className={`step ${isActive ? "active" : ""} ${isComplete ? "complete" : ""}`}
              onClick={() => onSetRunStep(step.id)}
            >
              <span className="step-index">{index + 1}</span>
              <span>
                <strong>{step.label}</strong>
                <small>{step.helper}</small>
              </span>
            </button>
          );
        })}
      </div>

      {runStep === "setup" && (
        <div className="grid">
          <section className="card span-7">
            <div className="card-header">
              <div>
                <h2>Source policy</h2>
                <span className="subtle">Choose the input PDF and destinations</span>
              </div>
            </div>

            <div className="field-group">
              <label>Policy PDF</label>
              <div className="field-row">
                <input
                  type="text"
                  value={config.pdfPath}
                  onChange={(event) => onUpdateConfig("pdfPath", event.target.value)}
                  disabled={config.revisionOnly}
                />
                <button
                  className="ghost"
                  onClick={onSelectPdf}
                  disabled={config.revisionOnly}
                >
                  Browse
                </button>
              </div>
            </div>

            <div className="field-group">
              <label>Output directory</label>
              <div className="field-row">
                <input
                  type="text"
                  value={config.outputDir}
                  onChange={(event) => onUpdateConfig("outputDir", event.target.value)}
                />
                <button className="ghost" onClick={onSelectOutputDir}>
                  Choose
                </button>
              </div>
              <p className="hint">Default: gap_analysis_reports</p>
            </div>

            <div className="field-group">
              <label>Run directory (reuse)</label>
              <div className="field-row">
                <input
                  type="text"
                  value={config.runDir}
                  onChange={(event) => onUpdateConfig("runDir", event.target.value)}
                  placeholder="gap_analysis_reports/20240101_120000"
                />
                <button className="ghost" onClick={onSelectRunDir}>
                  Select
                </button>
              </div>
              <p className="hint">
                Reuse a previous run directory to append results or review history.
              </p>
            </div>
          </section>

          <section className="card span-5">
            <div className="card-header">
              <div>
                <h2>Run summary</h2>
                <span className="subtle">Snapshot of settings</span>
              </div>
            </div>
            <div className="summary-grid">
              <div>
                <span className="meta-label">Policy</span>
                <strong>{policyFileName}</strong>
              </div>
              <div>
                <span className="meta-label">Output</span>
                <strong>{config.outputDir || "gap_analysis_reports"}</strong>
              </div>
              <div>
                <span className="meta-label">Run directory</span>
                <strong>{config.runDir || "Auto-generate"}</strong>
              </div>
              <div>
                <span className="meta-label">Provider</span>
                <strong>{config.provider}</strong>
              </div>
            </div>
            <div className="note">
              Continue to analysis settings to tune windowing and flags.
            </div>
          </section>
        </div>
      )}

      {runStep === "analysis" && (
        <div className="grid">
          <section className="card span-6">
            <div className="card-header">
              <div>
                <h2>Analysis parameters</h2>
                <span className="subtle">Chunk sizing + overlap</span>
              </div>
            </div>
            <div className="split">
              <div className="field-group">
                <label>Window size</label>
                <input
                  type="number"
                  min={20}
                  max={200}
                  value={config.windowSize}
                  onChange={(event) =>
                    onUpdateConfig("windowSize", Number(event.target.value))
                  }
                />
              </div>
              <div className="field-group">
                <label>Overlap</label>
                <input
                  type="number"
                  min={0}
                  max={50}
                  value={config.overlap}
                  onChange={(event) => onUpdateConfig("overlap", Number(event.target.value))}
                />
              </div>
            </div>
            <p className="hint">
              Larger windows capture more context but increase run time.
            </p>
          </section>

          <section className="card span-6">
            <div className="card-header">
              <div>
                <h2>Execution flags</h2>
                <span className="subtle">Optional run modes</span>
              </div>
            </div>
            <details className="collapsible">
              <summary>Advanced run options</summary>
              <div className="toggle-grid">
                <label className="toggle">
                  <input
                    type="checkbox"
                    checked={config.extractOnly}
                    onChange={(event) =>
                      onUpdateConfig("extractOnly", event.target.checked)
                    }
                  />
                  <span>Extract only</span>
                </label>
                <label className="toggle">
                  <input
                    type="checkbox"
                    checked={config.skipRevision}
                    onChange={(event) =>
                      onUpdateConfig("skipRevision", event.target.checked)
                    }
                  />
                  <span>Skip revision</span>
                </label>
                <label className="toggle">
                  <input
                    type="checkbox"
                    checked={config.skipExtraction}
                    onChange={(event) =>
                      onUpdateConfig("skipExtraction", event.target.checked)
                    }
                  />
                  <span>Skip extraction</span>
                </label>
                <label className="toggle">
                  <input
                    type="checkbox"
                    checked={config.revisionOnly}
                    onChange={(event) =>
                      onUpdateConfig("revisionOnly", event.target.checked)
                    }
                  />
                  <span>Revision only</span>
                </label>
              </div>
            </details>
            <p className="hint">
              Use advanced modes for partial reruns or revision-only outputs.
            </p>
          </section>
        </div>
      )}

      {runStep === "review" && (
        <div className="grid">
          <section className="card span-7">
            <div className="card-header">
              <div>
                <h2>Review and launch</h2>
                <span className="subtle">Final validation before running</span>
              </div>
            </div>
            {validation.length > 0 ? (
              <div className="alert warning">
                <strong>Ready check</strong>
                <ul>
                  {validation.map((issue) => (
                    <li key={issue}>{issue}</li>
                  ))}
                </ul>
              </div>
            ) : (
              <div className="empty">
                All required fields are set. Use the command bar above to start.
              </div>
            )}
            <div className="summary-grid">
              <div>
                <span className="meta-label">Policy</span>
                <strong>{policyFileName}</strong>
              </div>
              <div>
                <span className="meta-label">Model</span>
                <strong>{config.model}</strong>
              </div>
              <div>
                <span className="meta-label">Window</span>
                <strong>
                  {config.windowSize} / {config.overlap}
                </strong>
              </div>
              <div>
                <span className="meta-label">Flags</span>
                <strong>{activeFlags.length ? activeFlags.join(" · ") : "None"}</strong>
              </div>
            </div>
            <div className="note">
              Monitor the Live Telemetry screen while the run is active.
            </div>
          </section>

          <section className="card span-5">
            <div className="card-header">
              <div>
                <h2>Run status</h2>
                <span className="subtle">Execution visibility</span>
              </div>
            </div>
            <div className="stat-grid compact">
              <div className="stat">
                <span>Status</span>
                <strong>{runStateLabel}</strong>
              </div>
              <div className="stat">
                <span>PID</span>
                <strong>{statusEvent?.pid ?? "-"}</strong>
              </div>
              <div className="stat">
                <span>Exit</span>
                <strong>{exitInfo?.code ?? "-"}</strong>
              </div>
              <div className="stat">
                <span>Progress</span>
                <strong>{progressPct}%</strong>
              </div>
            </div>
            <div className="phase-list">
              {phases.map((phase) => (
                <div key={phase.id} className={`phase ${phase.status}`}>
                  <span>{phase.label}</span>
                  <strong>{phase.status}</strong>
                </div>
              ))}
            </div>
            <div className="inline-actions">
              <button className="ghost" onClick={onViewLogs} disabled={logsCount === 0}>
                View telemetry
              </button>
              <button className="ghost" onClick={onViewArtifacts} disabled={!config.runDir}>
                View artifacts
              </button>
            </div>
          </section>
        </div>
      )}

      <div className="step-actions">
        {prevRunStep && (
          <button className="ghost" onClick={() => onSetRunStep(prevRunStep)}>
            Back
          </button>
        )}
        {nextRunStep && (
          <button className="primary" onClick={() => onSetRunStep(nextRunStep)}>
            Continue
          </button>
        )}
      </div>
    </div>
  );
}

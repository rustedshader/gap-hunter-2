import React from "react";
import SegmentedTabs from "../components/SegmentedTabs";
import type { BackendEvent, LogEntry } from "../types";
import type { LogView } from "../types/ui";

type LevelFilter = {
  INFO: boolean;
  WARNING: boolean;
  ERROR: boolean;
  DEBUG: boolean;
};

type LogsViewProps = {
  logView: LogView;
  onSetLogView: (view: LogView) => void;
  filteredLogs: LogEntry[];
  events: BackendEvent[];
  levelFilter: LevelFilter;
  onSetLevelFilter: React.Dispatch<React.SetStateAction<LevelFilter>>;
  search: string;
  onSearchChange: (value: string) => void;
  autoScroll: boolean;
  onAutoScrollChange: (value: boolean) => void;
  showRawBackend: boolean;
  onShowRawBackendChange: (value: boolean) => void;
  logEndRef: React.RefObject<HTMLDivElement>;
  onClearLogs: () => void;
  onClearEvents: () => void;
};

export default function LogsView({
  logView,
  onSetLogView,
  filteredLogs,
  events,
  levelFilter,
  onSetLevelFilter,
  search,
  onSearchChange,
  autoScroll,
  onAutoScrollChange,
  showRawBackend,
  onShowRawBackendChange,
  logEndRef,
  onClearLogs,
  onClearEvents
}: LogsViewProps) {
  return (
    <div className="stack">
      <div className="page-tabs">
        <SegmentedTabs
          value={logView}
          onChange={onSetLogView}
          options={[
            { value: "stream", label: "Live logs" },
            { value: "events", label: "Structured events" }
          ]}
        />
        <div className="inline-actions">
          {logView === "stream" ? (
            <button className="ghost" onClick={onClearLogs}>
              Clear logs
            </button>
          ) : (
            <button className="ghost" onClick={onClearEvents}>
              Clear events
            </button>
          )}
        </div>
      </div>

      {logView === "stream" && (
        <section className="card">
          <div className="card-header">
            <div>
              <h2>Live logs</h2>
              <span className="subtle">Streaming telemetry</span>
            </div>
          </div>

          <div className="log-toolbar">
            <div className="log-filters">
              {Object.keys(levelFilter).map((level) => (
                <button
                  key={level}
                  className={
                    levelFilter[level as keyof LevelFilter]
                      ? "pill-btn active"
                      : "pill-btn"
                  }
                  onClick={() =>
                    onSetLevelFilter((prev) => ({
                      ...prev,
                      [level]: !prev[level as keyof LevelFilter]
                    }))
                  }
                >
                  {level}
                </button>
              ))}
            </div>
            <div className="log-tools">
              <input
                type="text"
                placeholder="Search logs"
                value={search}
                onChange={(event) => onSearchChange(event.target.value)}
              />
              <label className="toggle compact">
                <input
                  type="checkbox"
                  checked={autoScroll}
                  onChange={(event) => onAutoScrollChange(event.target.checked)}
                />
                <span>Auto-scroll</span>
              </label>
              <label className="toggle compact">
                <input
                  type="checkbox"
                  checked={showRawBackend}
                  onChange={(event) => onShowRawBackendChange(event.target.checked)}
                />
                <span>Show raw backend output</span>
              </label>
            </div>
          </div>

          <div className="log-panel">
            {filteredLogs.length === 0 ? (
              <div className="empty">No log activity yet.</div>
            ) : (
              filteredLogs.map((entry, index) => (
                <div
                  key={`${entry.time}-${index}`}
                  className={`log-line ${entry.level.toLowerCase()}`}
                >
                  <span className="log-time">{entry.time}</span>
                  <span className="log-level">{entry.level}</span>
                  <span className="log-message">
                    <strong>{entry.logger}</strong> {entry.message}
                  </span>
                </div>
              ))
            )}
            <div ref={logEndRef} />
          </div>
        </section>
      )}

      {logView === "events" && (
        <section className="card">
          <div className="card-header">
            <div>
              <h2>Structured events</h2>
              <span className="subtle">Pipeline milestones</span>
            </div>
          </div>
          {events.length === 0 ? (
            <div className="empty">No structured events yet.</div>
          ) : (
            <div className="event-grid">
              {events.slice(-30).map((event, index) => {
                const details = Object.entries(event).filter(
                  ([key]) => key !== "name" && key !== "timestamp"
                );
                return (
                  <div key={`${event.name}-${index}`} className="event-card">
                    <div className="event-header">
                      <strong>{event.name}</strong>
                      <span className="subtle">{event.timestamp || ""}</span>
                    </div>
                    {details.length > 0 && (
                      <div className="event-meta">
                        {details.slice(0, 4).map(([key, value]) => (
                          <div key={key}>
                            <span className="meta-label">{key}</span>
                            <strong>{String(value)}</strong>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </section>
      )}
    </div>
  );
}

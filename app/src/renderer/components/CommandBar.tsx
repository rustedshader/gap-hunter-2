import React, { useEffect, useRef, useState } from "react";
import type { ExitEvent, StatusEvent } from "../types";

type CommandBarProps = {
  runOutcomeTone: "idle" | "live" | "warning" | "error";
  runOutcomeLabel: string;
  statusEvent: StatusEvent | null;
  exitInfo: ExitEvent | null;
  progressPct: number;
  runDir: string;
  provider: string;
  startDisabled: boolean;
  isRunning: boolean;
  canClearStatus: boolean;
  onStart: () => void;
  onStop: () => void;
  onForceStop: () => void;
  onClearStatus: () => void;
  onOpenRunDir: () => void;
};

export default function CommandBar({
  runOutcomeTone,
  runOutcomeLabel,
  statusEvent,
  exitInfo,
  progressPct,
  runDir,
  provider,
  startDisabled,
  isRunning,
  canClearStatus,
  onStart,
  onStop,
  onForceStop,
  onClearStatus,
  onOpenRunDir
}: CommandBarProps) {
  const [isCompact, setIsCompact] = useState(true);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!isMenuOpen) {
      return;
    }

    const handleClick = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [isMenuOpen]);

  return (
    <section className={`command-bar${isCompact ? " compact" : ""}`}>
      <div className="command-main">
        <div className="command-row">
          <div className={`status-pill ${runOutcomeTone}`}>
            <span className="status-dot" />
            <span>{runOutcomeLabel}</span>
          </div>
          <div className="command-meta">
            <span>PID: {statusEvent?.pid ?? "-"}</span>
            <span>Exit: {exitInfo?.code ?? "-"}</span>
            <span>Progress: {progressPct}%</span>
          </div>
        </div>
        <div className="command-row command-row-secondary">
          <div className="progress">
            <div className="progress-bar" style={{ width: `${progressPct}%` }} />
          </div>
          {!isCompact && (
            <div className="command-path">
              <div>
                <span className="meta-label">Run directory</span>
                <strong>{runDir || "Not set"}</strong>
              </div>
              <div>
                <span className="meta-label">Provider</span>
                <strong>{provider}</strong>
              </div>
            </div>
          )}
        </div>
      </div>
      <div className="command-actions">
        <div className="action-group">
          <button className="primary" onClick={onStart} disabled={startDisabled}>
            Start run
          </button>
          <button className="ghost" onClick={onStop} disabled={!isRunning}>
            Stop
          </button>
        </div>
        <div className="action-group">
          <button
            className="ghost"
            onClick={() => setIsCompact((prev) => !prev)}
            aria-expanded={!isCompact}
          >
            {isCompact ? "Show details" : "Hide details"}
          </button>
          <div className="command-overflow" ref={menuRef}>
            <button
              className="ghost"
              onClick={() => setIsMenuOpen((prev) => !prev)}
              aria-haspopup="menu"
              aria-expanded={isMenuOpen}
            >
              More
            </button>
            {isMenuOpen && (
              <div className="command-overflow-menu" role="menu">
                <button
                  className="menu-button"
                  role="menuitem"
                  onClick={() => {
                    onOpenRunDir();
                    setIsMenuOpen(false);
                  }}
                  disabled={!runDir}
                >
                  Open run folder
                </button>
                <button
                  className="menu-button"
                  role="menuitem"
                  onClick={() => {
                    onClearStatus();
                    setIsMenuOpen(false);
                  }}
                  disabled={!canClearStatus}
                >
                  Clear status
                </button>
                <button
                  className="menu-button danger"
                  role="menuitem"
                  onClick={() => {
                    onForceStop();
                    setIsMenuOpen(false);
                  }}
                  disabled={!isRunning}
                >
                  Force stop
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

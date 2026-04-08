import React from "react";
import { NAV_GROUPS, VIEW_META } from "../constants";
import type { AppConfig, View } from "../types/ui";

type SidebarProps = {
  activeView: View;
  onSelectView: (view: View) => void;
  runStateLabel: string;
  config: AppConfig;
};

export default function Sidebar({
  activeView,
  onSelectView,
  runStateLabel,
  config
}: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">GH</div>
        <div>
          <div className="brand-title">Gap Hunter Studio</div>
          <div className="brand-subtitle">Policy gap analysis</div>
        </div>
      </div>

      <nav className="nav">
        {NAV_GROUPS.map((group) => (
          <div key={group.label} className="nav-group">
            <div className="nav-group-title">{group.label}</div>
            {group.items.map((item) => (
              <button
                key={item}
                className={`nav-button ${activeView === item ? "active" : ""}`}
                onClick={() => onSelectView(item)}
              >
                <span className="nav-dot" />
                <span>{VIEW_META[item].title}</span>
              </button>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className={`status-pill ${runStateLabel === "Running" ? "live" : "idle"}`}>
          <span className="status-dot" />
          <span>{runStateLabel}</span>
        </div>
        <div className="sidebar-meta">
          <span>Provider: {config.provider}</span>
          <span>Model: {config.model}</span>
        </div>
      </div>
    </aside>
  );
}

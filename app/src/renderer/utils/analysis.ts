import type {
  AssessmentStatus,
  PolicySection,
  RevisionReport,
  RoadmapData,
  StatusCounts,
  SubcategoryAssessment
} from "../types/ui";

export function buildEvidenceMap(
  sections: PolicySection[],
  assessments: Record<string, SubcategoryAssessment[]>
) {
  const map: Record<string, SubcategoryAssessment[]> = {};
  sections.forEach((section) => {
    map[section.number] = [];
  });
  map.unmapped = [];

  Object.values(assessments)
    .flat()
    .forEach((assessment) => {
      const snippet = normalizeEvidence(assessment.evidence);
      if (!snippet) {
        return;
      }

      const snippetLower = snippet.toLowerCase();
      let matched = false;
      for (const section of sections) {
        const content = (section.content || "").toLowerCase();
        if (content.includes(snippetLower)) {
          map[section.number].push(assessment);
          matched = true;
        }
      }
      if (!matched) {
        map.unmapped.push(assessment);
      }
    });

  return map;
}

export function normalizeEvidence(evidence: string) {
  if (!evidence) {
    return "";
  }
  const lowered = evidence.toLowerCase();
  if (
    lowered.includes("no relevant") ||
    lowered.includes("none found") ||
    lowered.includes("n/a")
  ) {
    return "";
  }
  return evidence.trim().slice(0, 120);
}

export function getSectionTitle(sections: PolicySection[] | undefined, number: string | null) {
  if (!sections || !number) {
    return "";
  }
  return sections.find((s) => s.number === number)?.title || "";
}

export function getSectionContent(sections: PolicySection[] | undefined, number: string | null) {
  if (!sections || !number) {
    return "";
  }
  return sections.find((s) => s.number === number)?.content || "";
}

export function getFunctionSummary(
  assessments: Record<string, SubcategoryAssessment[]> | undefined,
  functionName: string
) {
  if (!assessments) {
    return "No data";
  }
  const items = assessments[functionName] || [];
  if (items.length === 0) {
    return "No data";
  }
  const inScope = items.filter((item) => item.status !== "Out of Scope");
  const notAddressed = inScope.filter((item) => item.status === "Not Addressed").length;
  const partial = inScope.filter((item) => item.status === "Partially Addressed").length;
  const addressed = inScope.filter((item) => item.status === "Addressed").length;
  return `${addressed} addressed, ${partial} partial, ${notAddressed} gaps`;
}

export function buildOriginalPolicy(sections: PolicySection[]) {
  if (!sections.length) {
    return "No sections available.";
  }
  const lines: string[] = ["# Original Policy\n"];
  sections.forEach((section) => {
    lines.push(`## ${section.number}. ${section.title}`);
    lines.push(section.content || "");
    lines.push("\n---\n");
  });
  return lines.join("\n");
}

export function parseRevisionReport(markdown: string): RevisionReport {
  const lines = markdown.split(/\r?\n/);
  let totalGaps = 0;
  let modifiedSections = 0;
  let newSections = 0;
  const changes: RevisionReport["changes"] = [];
  let inChangesTable = false;

  for (const line of lines) {
    if (line.startsWith("- **Total gaps addressed**:")) {
      totalGaps = Number.parseInt(line.replace(/[^0-9]/g, ""), 10) || 0;
    }
    if (line.startsWith("- **Sections modified**:")) {
      modifiedSections = Number.parseInt(line.replace(/[^0-9]/g, ""), 10) || 0;
    }
    if (line.startsWith("- **New sections added**:")) {
      newSections = Number.parseInt(line.replace(/[^0-9]/g, ""), 10) || 0;
    }

    if (line.startsWith("## Changes")) {
      inChangesTable = true;
      continue;
    }
    if (inChangesTable && line.startsWith("## ")) {
      inChangesTable = false;
    }
    if (inChangesTable && line.startsWith("|") && !line.includes("---")) {
      const cells = line
        .split("|")
        .map((cell) => cell.trim())
        .filter(Boolean);
      if (cells.length >= 5) {
        changes.push({
          id: cells[1],
          action: cells[2],
          section: cells[3],
          description: cells[4]
        });
      }
    }
  }

  return { totalGaps, modifiedSections, newSections, changes };
}

export function parseRoadmap(markdown: string): RoadmapData {
  const lines = markdown.split(/\r?\n/);
  let executiveSummary = "";
  const tiers: RoadmapData["tiers"] = [];
  const missingDocs: string[] = [];

  let currentTier: RoadmapData["tiers"][number] | null = null;
  let currentItem: RoadmapData["tiers"][number]["items"][number] | null = null;
  let mode: "summary" | "tier" | "docs" | null = null;

  for (const line of lines) {
    if (line.startsWith("## Executive Summary")) {
      mode = "summary";
      continue;
    }
    if (line.startsWith("## Missing Policy Documents")) {
      mode = "docs";
      currentTier = null;
      currentItem = null;
      continue;
    }
    if (line.startsWith("## ") && !line.includes("Executive Summary")) {
      mode = "tier";
      const tierName = line.replace("## ", "").trim();
      currentTier = { tierName, rationale: "", items: [] };
      tiers.push(currentTier);
      continue;
    }
    if (mode === "tier" && line.startsWith("*")) {
      if (currentTier) {
        currentTier.rationale = line.replace(/\*/g, "").trim();
      }
      continue;
    }
    if (mode === "tier" && line.startsWith("### ")) {
      const title = line.replace("### ", "").trim();
      currentItem = {
        title,
        nistReference: "",
        description: "",
        responsible: "",
        effort: "",
        successCriteria: "",
        dependencies: ""
      };
      currentTier?.items.push(currentItem);
      continue;
    }
    if (mode === "tier" && line.startsWith("- **") && currentItem) {
      const [label, value] = line.split("**:");
      const cleanValue = (value || "").trim();
      if (label.includes("NIST Reference")) {
        currentItem.nistReference = cleanValue;
      } else if (label.includes("Description")) {
        currentItem.description = cleanValue;
      } else if (label.includes("Responsible")) {
        currentItem.responsible = cleanValue;
      } else if (label.includes("Effort")) {
        currentItem.effort = cleanValue;
      } else if (label.includes("Success Criteria")) {
        currentItem.successCriteria = cleanValue;
      } else if (label.includes("Dependencies")) {
        currentItem.dependencies = cleanValue;
      }
    }

    if (mode === "summary" && line.trim()) {
      executiveSummary += `${line.trim()} `;
    }

    if (mode === "docs" && /^\d+\./.test(line.trim())) {
      missingDocs.push(line.replace(/^\d+\./, "").trim());
    }
  }

  return {
    executiveSummary: executiveSummary.trim(),
    tiers,
    missingDocs
  };
}

export function statusClass(status: AssessmentStatus) {
  switch (status) {
    case "Addressed":
      return "status-success";
    case "Partially Addressed":
      return "status-warning";
    case "Not Addressed":
      return "status-danger";
    default:
      return "status-muted";
  }
}

export function summarizeAssessments(items: SubcategoryAssessment[]): StatusCounts {
  const total = items.length;
  const addressed = items.filter((item) => item.status === "Addressed").length;
  const partiallyAddressed = items.filter(
    (item) => item.status === "Partially Addressed"
  ).length;
  const notAddressed = items.filter(
    (item) => item.status === "Not Addressed"
  ).length;
  const outOfScope = items.filter((item) => item.status === "Out of Scope").length;
  return { total, addressed, partiallyAddressed, notAddressed, outOfScope };
}

export function formatBytes(bytes: number) {
  if (Number.isNaN(bytes)) {
    return "-";
  }
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  const kb = bytes / 1024;
  if (kb < 1024) {
    return `${kb.toFixed(1)} KB`;
  }
  const mb = kb / 1024;
  return `${mb.toFixed(1)} MB`;
}

export function formatDateTime(value: string | number | null | undefined) {
  if (!value) {
    return "-";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "-";
  }
  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  });
}

export function formatDuration(durationMs: number | null | undefined) {
  if (!durationMs || !Number.isFinite(durationMs)) {
    return "-";
  }
  const totalSeconds = Math.max(0, Math.floor(durationMs / 1000));
  const seconds = totalSeconds % 60;
  const totalMinutes = Math.floor(totalSeconds / 60);
  const minutes = totalMinutes % 60;
  const hours = Math.floor(totalMinutes / 60);

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  if (minutes > 0) {
    return `${minutes}m ${seconds}s`;
  }
  return `${seconds}s`;
}

export function truncate(text: string, maxLength: number) {
  if (!text) {
    return "";
  }
  if (text.length <= maxLength) {
    return text;
  }
  return `${text.slice(0, maxLength)}...`;
}


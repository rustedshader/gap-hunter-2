export type FaqItem = {
  id: string;
  question: string;
  answer: string;
  bullets?: string[];
  related?: string[];
  keywords?: string[];
};

export type FaqSection = {
  id: string;
  title: string;
  description?: string;
  items: FaqItem[];
};

export const FAQ_SECTIONS: FaqSection[] = [
  {
    id: "general",
    title: "General",
    description: "Foundations of Gap Hunter Studio.",
    items: [
      {
        id: "what-is-gap-hunter",
        question: "What is Gap Hunter Studio?",
        answer:
          "Gap Hunter Studio is a local desktop app for running policy gap analysis against the CIS MS-ISAC NIST CSF Policy Template Guide (2024).",
        related: ["what-does-app-do", "does-it-need-internet"]
      },
      {
        id: "what-does-app-do",
        question: "What does the app do?",
        answer:
          "It extracts sections from a policy PDF, analyzes coverage against NIST CSF subcategories, summarizes gaps, and can generate revision and roadmap artifacts when enabled.",
        related: ["what-happens-on-start", "what-is-gap-matrix"]
      },
      {
        id: "who-is-it-for",
        question: "Who is this app for?",
        answer:
          "Security teams, compliance teams, and auditors who need repeatable gap analysis of policy documents with clear evidence trails.",
        related: ["what-is-evidence-explorer"]
      },
      {
        id: "does-it-need-internet",
        question: "Does the app require internet access?",
        answer:
          "No. Gap Hunter Studio is designed to run offline with local model providers. Internet is optional and only needed if your model provider requires it.",
        related: ["does-it-call-external-api", "does-demo-call-llm"]
      },
      {
        id: "does-it-call-external-api",
        question: "Does it make external API calls?",
        answer:
          "Only if you configure a provider that requires it. The default local workflow keeps data on your machine.",
        related: ["what-data-stays-local"]
      },
      {
        id: "what-data-stays-local",
        question: "What data stays local?",
        answer:
          "Input PDFs, extracted sections, analysis artifacts, logs, and run history are stored locally in your run directory.",
        related: ["where-are-runs-stored"]
      },
      {
        id: "what-is-run",
        question: "What is a run?",
        answer:
          "A run is a single execution of the pipeline. It has a run directory containing outputs, logs, and metadata so you can return later.",
        related: ["where-are-runs-stored", "can-i-reopen-run"]
      }
    ]
  },
  {
    id: "input-setup",
    title: "Input and Setup",
    description: "Choosing files and configuring a run.",
    items: [
      {
        id: "what-input-files",
        question: "What kind of policy files can I use?",
        answer: "The Run Builder accepts PDF policy documents. Use text-based PDFs for best results.",
        related: ["pdf-scanned"]
      },
      {
        id: "pdf-scanned",
        question: "What happens if my PDF is scanned or malformed?",
        answer:
          "Scanned PDFs can lead to poor extraction. If sections look empty or garbled, re-export the PDF with OCR or supply a text-based version.",
        related: ["why-no-artifacts", "what-if-bad-extract"]
      },
      {
        id: "what-is-output-dir",
        question: "What does output directory mean?",
        answer:
          "It is the parent folder where new run folders are created. Each run gets its own subfolder with outputs.",
        related: ["what-is-run-dir"]
      },
      {
        id: "what-is-run-dir",
        question: "What is run directory reuse?",
        answer:
          "You can point the run to an existing run directory to append or revisit outputs. This is useful for revision-only or partial runs.",
        related: ["revision-only"]
      },
      {
        id: "window-overlap",
        question: "What do window size and overlap mean?",
        answer:
          "These control how the policy text is chunked for analysis. Larger windows capture more context, overlap keeps continuity between chunks.",
        related: ["first-run-config"]
      },
      {
        id: "run-flags",
        question: "What do extract only, skip extraction, skip revision, and revision only do?",
        answer: "These flags control which phases run.",
        bullets: [
          "Extract only: parse the policy but skip analysis and revision.",
          "Skip extraction: use an existing run directory with extracted sections.",
          "Skip revision: run analysis only, no revision outputs.",
          "Revision only: generate revisions from an existing run directory."
        ],
        related: ["revision-only", "what-happens-on-start"]
      },
      {
        id: "first-run-config",
        question: "How should I configure a first run?",
        answer:
          "Start with a text-based PDF, leave run directory blank, and keep default window settings. You can refine settings after the first run.",
        related: ["window-overlap", "what-happens-on-start"]
      },
      {
        id: "invalid-path",
        question: "What if my input file path is invalid?",
        answer:
          "The run will fail validation. Use the Browse button to reselect the PDF and confirm the path exists.",
        related: ["why-run-not-starting"]
      }
    ]
  },
  {
    id: "execution",
    title: "Execution",
    description: "What happens during a run.",
    items: [
      {
        id: "what-happens-on-start",
        question: "What happens when I click Start run?",
        answer:
          "The backend launches, creates a run folder, extracts sections, performs gap analysis, and writes artifacts to the run directory.",
        related: ["what-is-run", "why-run-slow"]
      },
      {
        id: "stop-vs-force",
        question: "What is the difference between Stop and Force stop?",
        answer:
          "Stop requests a graceful shutdown. Force stop terminates the backend process if it does not exit quickly.",
        related: ["can-i-close-app"]
      },
      {
        id: "why-run-slow",
        question: "Why is my run taking a long time?",
        answer:
          "Large PDFs, slower models, and smaller chunk sizes can increase processing time. Check Live Telemetry for activity.",
        related: ["progress-stays-zero", "what-is-live-telemetry"]
      },
      {
        id: "progress-stays-zero",
        question: "Why does progress stay at 0 for some time?",
        answer:
          "Early phases can take time before the first milestones are logged. Progress updates when phases report completion.",
        related: ["what-is-live-telemetry"]
      },
      {
        id: "what-is-pid",
        question: "What does PID mean?",
        answer:
          "PID is the process ID of the backend run. It helps with debugging and system monitoring.",
        related: ["what-is-exit"]
      },
      {
        id: "what-is-exit",
        question: "What does Exit mean?",
        answer:
          "Exit is the backend process exit code. A value of 0 usually means success; non-zero means failure.",
        related: ["failed-run"]
      },
      {
        id: "can-i-close-app",
        question: "Can I close the app while a run is active?",
        answer:
          "You can, but active runs may be marked as cancelled or orphaned. Use Stop when possible to keep run state clean.",
        related: ["stop-vs-force"]
      },
      {
        id: "crash-behavior",
        question: "What happens if the app crashes?",
        answer:
          "The run history is preserved. On restart the app attempts to recover and mark runs as completed, failed, or orphaned.",
        related: ["failed-run", "run-history-durable"]
      },
      {
        id: "failed-run",
        question: "How are failed runs shown?",
        answer:
          "Failed runs are labeled in the Run Library and in status badges. Open the run to view logs and artifacts.",
        related: ["how-to-inspect-logs", "why-no-artifacts"]
      }
    ]
  },
  {
    id: "results",
    title: "Results and Analysis",
    description: "Understanding outputs and analysis screens.",
    items: [
      {
        id: "what-is-evidence-explorer",
        question: "What is Evidence Explorer?",
        answer:
          "Evidence Explorer maps NIST subcategory assessments to policy sections so you can see which text supports each assessment.",
        related: ["evidence-no-matches", "coverage-status"]
      },
      {
        id: "what-is-gap-matrix",
        question: "What is Gap Matrix?",
        answer:
          "Gap Matrix provides a coverage grid by NIST function and subcategory. It helps you spot gaps quickly.",
        related: ["coverage-status"]
      },
      {
        id: "what-is-revision-diff",
        question: "What is Revision Diff Studio?",
        answer:
          "Revision Diff Studio compares the original policy to the revised policy output produced by the revision phase.",
        related: ["how-to-know-revision", "revision-only"]
      },
      {
        id: "what-is-roadmap",
        question: "What is Roadmap Planner?",
        answer:
          "Roadmap Planner lists prioritized initiatives and missing policy documents to close the identified gaps.",
        related: ["how-to-know-revision"]
      },
      {
        id: "interpret-evidence",
        question: "How should I interpret evidence matches?",
        answer:
          "Each assessment includes evidence snippets from the policy. If no evidence is found, the assessment is likely a gap.",
        related: ["evidence-no-matches", "coverage-status"]
      },
      {
        id: "evidence-no-matches",
        question: "Why does a section show no evidence?",
        answer:
          "Some sections may not match any NIST subcategories. Use the status filter to review gaps or out-of-scope items.",
        related: ["what-is-evidence-explorer"]
      },
      {
        id: "coverage-status",
        question: "What does Addressed, Partially Addressed, Not Addressed, and Out of Scope mean?",
        answer:
          "These labels describe how well the policy covers each NIST subcategory based on evidence.",
        bullets: [
          "Addressed: evidence clearly meets the requirement.",
          "Partially Addressed: evidence exists but is incomplete.",
          "Not Addressed: no relevant evidence was found.",
          "Out of Scope: the subcategory does not apply to this policy."
        ],
        related: ["what-is-gap-matrix"]
      },
      {
        id: "panels-empty",
        question: "What happens if a run finishes but some panels show no data?",
        answer:
          "Missing artifacts or filtered views can cause empty panels. Check the Run Library for missing files and refresh artifacts.",
        related: ["why-no-artifacts", "run-history-missing-files"]
      },
      {
        id: "how-to-know-revision",
        question: "How do I know if revision output was generated?",
        answer:
          "The Run Library shows whether revision artifacts are present. The Revision Diff Studio will show a report when available.",
        related: ["what-is-revision-diff", "run-history-metadata"]
      }
    ]
  },
  {
    id: "run-history",
    title: "Run Library and Artifacts",
    description: "Preserving and revisiting past runs.",
    items: [
      {
        id: "where-are-runs-stored",
        question: "Where are past runs stored?",
        answer:
          "Runs are saved under the output directory you choose. Each run has its own timestamped folder.",
        related: ["run-history-durable"]
      },
      {
        id: "run-history-durable",
        question: "Will my past runs stay available?",
        answer:
          "Yes. The app stores a durable run index so history persists across restarts unless you delete a run.",
        related: ["can-i-delete-run"]
      },
      {
        id: "can-i-reopen-run",
        question: "Can I reopen an old run?",
        answer:
          "Yes. Select it in the Run Library to load its data and artifacts into the viewers.",
        related: ["what-is-run"]
      },
      {
        id: "can-i-delete-run",
        question: "Can I delete a run?",
        answer:
          "Yes. The Run Details panel lets you remove a run from the library or delete the run folder entirely.",
        related: ["run-history-missing-files"]
      },
      {
        id: "run-history-missing-files",
        question: "What happens if I delete files outside the app?",
        answer:
          "The run remains in history but will show missing artifacts. You can restore files or remove the run entry.",
        related: ["run-history-metadata"]
      },
      {
        id: "compare-runs",
        question: "Can I compare old and new runs?",
        answer:
          "You can open runs side by side in the library and compare counts or artifacts manually. Dedicated compare tooling may be added later.",
        related: ["run-history-metadata"]
      },
      {
        id: "reuse-run",
        question: "Can I reuse a past run's outputs?",
        answer:
          "Yes. Use Run Builder and select a run directory to reuse extracted sections or revision outputs.",
        related: ["what-is-run-dir"]
      },
      {
        id: "pin-run",
        question: "What does pinning a run do?",
        answer:
          "Pinned runs stay at the top of the library and are easier to find in long histories.",
        related: ["run-history-durable"]
      },
      {
        id: "run-history-metadata",
        question: "What metadata is tracked for each run?",
        answer:
          "The library stores status, timestamps, model, provider, counts, and artifact availability. Notes and tags are user-editable.",
        related: ["run-history-durable"]
      }
    ]
  },
  {
    id: "models",
    title: "Models and Runtime",
    description: "Providers, models, and offline behavior.",
    items: [
      {
        id: "which-model",
        question: "Which model is being used?",
        answer:
          "The active provider and model name are shown in the sidebar and on the dashboard. You can change them in Settings.",
        related: ["why-model-matters"]
      },
      {
        id: "why-model-matters",
        question: "Why does model selection matter?",
        answer:
          "Models vary in quality and speed. Larger models may improve reasoning but require more time and memory.",
        related: ["why-run-slow"]
      },
      {
        id: "model-unavailable",
        question: "What happens if the model is unavailable?",
        answer:
          "The run will fail to start or stop early. Check provider status and model availability in Settings.",
        related: ["why-run-not-starting"]
      },
      {
        id: "ollama-vs-gguf",
        question: "What is the difference between Ollama and local GGUF?",
        answer:
          "Ollama runs models via a local HTTP service. Local GGUF runs models directly from a file path.",
        related: ["does-it-need-internet"]
      },
      {
        id: "does-demo-call-llm",
        question: "Does demo mode use the model?",
        answer:
          "No. Demo mode uses precomputed data and never calls a model or launches the backend.",
        related: ["what-is-demo-mode"]
      },
      {
        id: "does-app-call-llm",
        question: "Does the app make LLM calls in all workflows?",
        answer:
          "Only real runs use the model. Library browsing, demo mode, and viewing artifacts do not.",
        related: ["what-is-demo-mode"]
      },
      {
        id: "fully-offline",
        question: "Can I run fully offline?",
        answer:
          "Yes. Use a local provider and keep all artifacts on disk. The app does not require a network connection.",
        related: ["does-it-need-internet"]
      }
    ]
  },
  {
    id: "troubleshooting",
    title: "Troubleshooting",
    description: "Common issues and fixes.",
    items: [
      {
        id: "why-run-not-starting",
        question: "Why is the run not starting?",
        answer:
          "Check the validation panel for missing inputs, verify the PDF path, and confirm the model provider is reachable.",
        related: ["invalid-path", "model-unavailable"]
      },
      {
        id: "why-no-artifacts",
        question: "Why are no artifacts showing?",
        answer:
          "The run might still be active, or the run folder is missing files. Refresh artifacts or rescan the output directory.",
        related: ["run-history-missing-files"]
      },
      {
        id: "why-stale-ui",
        question: "Why is the UI showing stale-looking data?",
        answer:
          "Auto refresh may be off, or the run data has not been reloaded. Use Refresh in Artifacts or toggle auto refresh in Settings.",
        related: ["how-refresh-results"]
      },
      {
        id: "run-stuck",
        question: "What should I do if a run seems stuck?",
        answer:
          "Check Live Telemetry for log activity. If there is no progress for a long time, try Stop, then Force stop.",
        related: ["stop-vs-force"]
      },
      {
        id: "how-refresh-results",
        question: "How do I refresh results?",
        answer:
          "Use Refresh in the Artifacts view or open the Run Library and select the run again to reload metadata.",
        related: ["why-no-artifacts"]
      },
      {
        id: "what-if-bad-extract",
        question: "What if a PDF extracts badly?",
        answer:
          "Try a cleaned or OCR version of the PDF. Ensure the policy has clear headings and sections.",
        related: ["pdf-scanned"]
      },
      {
        id: "failed-or-partial",
        question: "What if I see a failed or partial run?",
        answer:
          "Open the run in the library to see which artifacts exist. You can reuse the run directory to complete missing phases.",
        related: ["run-history-missing-files"]
      },
      {
        id: "how-to-inspect-logs",
        question: "How do I inspect logs?",
        answer:
          "Use Live Telemetry for streaming logs and Diagnostics for debug logs saved to the run directory.",
        related: ["what-is-live-telemetry"]
      },
      {
        id: "what-is-live-telemetry",
        question: "What is Live Telemetry?",
        answer:
          "Live Telemetry streams backend logs and structured events so you can monitor progress and troubleshoot issues.",
        related: ["why-run-slow"]
      }
    ]
  },
  {
    id: "demo",
    title: "Demo Mode",
    description: "Guided walkthrough using precomputed data.",
    items: [
      {
        id: "what-is-demo-mode",
        question: "What is demo mode?",
        answer:
          "Demo mode is a guided, offline walkthrough of the full workflow using a pre-generated sample run.",
        related: ["does-demo-call-llm"]
      },
      {
        id: "demo-real-analysis",
        question: "Is demo mode real analysis?",
        answer:
          "No. Demo mode replays stored artifacts and explanations so you can learn the workflow without running the pipeline.",
        related: ["does-demo-call-llm"]
      },
      {
        id: "demo-sample-run",
        question: "What sample run is being shown?",
        answer:
          "The demo uses a bundled sample run stored with the app or an existing local sample run when available.",
        related: ["where-are-runs-stored"]
      },
      {
        id: "demo-interactive",
        question: "Can I interact with the demo?",
        answer:
          "Yes. You can step through the workflow and open the demo data in the normal viewers.",
        related: ["can-i-reopen-run"]
      },
      {
        id: "demo-exit",
        question: "Can I exit demo mode and run the real pipeline?",
        answer:
          "Yes. Use Run Builder to configure a real run. Demo mode never changes your real runs.",
        related: ["first-run-config"]
      }
    ]
  }
];

export const GLOSSARY = [
  {
    term: "Run",
    definition: "A single execution of the analysis pipeline with its own outputs and metadata."
  },
  {
    term: "Run directory",
    definition: "The folder where artifacts for a run are stored."
  },
  {
    term: "Output directory",
    definition: "The parent folder that contains run directories."
  },
  {
    term: "Artifact",
    definition: "A file created by the run, such as summaries, reports, or logs."
  },
  {
    term: "Assessment",
    definition: "An evaluation of a NIST subcategory against the policy content."
  },
  {
    term: "Evidence",
    definition: "A text snippet that supports an assessment."
  },
  {
    term: "Gap",
    definition: "A missing or incomplete requirement based on the assessment results."
  },
  {
    term: "Revision",
    definition: "A suggested policy update that closes one or more gaps."
  },
  {
    term: "Roadmap",
    definition: "A prioritized list of initiatives or documents to close identified gaps."
  },
  {
    term: "Master list",
    definition: "A structured list of extracted policy sections."
  },
  {
    term: "Coverage",
    definition: "The overall status distribution across NIST subcategories."
  }
];

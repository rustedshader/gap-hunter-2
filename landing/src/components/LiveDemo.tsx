"use client";

import { useState, useEffect } from "react";
import { Play, FileText, CheckCircle2, AlertCircle, Clock, Download, Eye, Pause } from "lucide-react";

export function LiveDemo() {
  const [activeDemo, setActiveDemo] = useState<"extraction" | "analysis" | "remediation">("extraction");
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (isPlaying) {
      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 100) {
            setIsPlaying(false);
            return 100;
          }
          return prev + 2;
        });
      }, 100);
      return () => clearInterval(interval);
    } else {
      setProgress(0);
    }
  }, [isPlaying]);

  return (
    <section className="py-24 bg-gradient-to-b from-slate-50 to-white" id="demo">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-100 text-purple-800 rounded-full text-sm font-semibold mb-4">
            <Play className="w-4 h-4" />
            See It In Action
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
            Watch Gap Hunter 2 Work
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Real examples from our golden dataset showing the complete pipeline in action
          </p>
        </div>

        {/* Demo Selector */}
        <div className="flex flex-wrap justify-center gap-4 mb-12">
          <DemoButton
            active={activeDemo === "extraction"}
            onClick={() => setActiveDemo("extraction")}
            label="Phase 1: Extraction"
            duration="~30 seconds"
          />
          <DemoButton
            active={activeDemo === "analysis"}
            onClick={() => setActiveDemo("analysis")}
            label="Phase 2: Gap Analysis"
            duration="~2 minutes"
          />
          <DemoButton
            active={activeDemo === "remediation"}
            onClick={() => setActiveDemo("remediation")}
            label="Phase 3: Remediation"
            duration="~3 minutes"
          />
        </div>

        {/* Demo Content */}
        <div className="bg-white rounded-2xl shadow-2xl overflow-hidden border border-slate-200">
          {/* Demo Header */}
          <div className="bg-gradient-to-r from-slate-800 to-slate-900 p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold mb-1">
                  {activeDemo === "extraction" && "Document Extraction Pipeline"}
                  {activeDemo === "analysis" && "Multi-Agent Gap Analysis"}
                  {activeDemo === "remediation" && "Automated Policy Remediation"}
                </h3>
                <p className="text-slate-300 text-sm">
                  {activeDemo === "extraction" && "Processing: information_security_iwu.pdf"}
                  {activeDemo === "analysis" && "Analyzing against NIST CSF 2.0 Framework"}
                  {activeDemo === "remediation" && "Generating compliant policy revision"}
                </p>
              </div>
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="px-6 py-3 bg-emerald-500 hover:bg-emerald-600 rounded-lg font-semibold flex items-center gap-2 transition-colors"
              >
                {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                {isPlaying ? "Pause" : "Run Demo"}
              </button>
            </div>
            {/* Progress Bar */}
            {isPlaying && (
              <div className="mt-4 w-full bg-slate-700 rounded-full h-2 overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-emerald-400 to-blue-400 transition-all duration-100"
                  style={{ width: `${progress}%` }}
                />
              </div>
            )}
          </div>

          {/* Demo Body */}
          <div className="p-8">
            {activeDemo === "extraction" && <ExtractionDemo />}
            {activeDemo === "analysis" && <AnalysisDemo />}
            {activeDemo === "remediation" && <RemediationDemo />}
          </div>

          {/* Demo Footer */}
          <div className="bg-slate-50 p-6 border-t border-slate-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-slate-500" />
                  <span className="text-slate-600">
                    {activeDemo === "extraction" && "Completed in 28 seconds"}
                    {activeDemo === "analysis" && "Completed in 1m 47s"}
                    {activeDemo === "remediation" && "Completed in 2m 53s"}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  <span className="text-slate-600">All validations passed</span>
                </div>
              </div>
              <div className="flex gap-3">
                <button className="px-4 py-2 border border-slate-300 rounded-lg text-sm font-semibold hover:bg-slate-50 flex items-center gap-2">
                  <Eye className="w-4 h-4" />
                  View Logs
                </button>
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 flex items-center gap-2">
                  <Download className="w-4 h-4" />
                  Download Results
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Sample Outputs */}
        <div className="mt-16 grid md:grid-cols-3 gap-6">
          <SampleOutput
            title="sections_output.json"
            description="57 sections extracted with line-perfect boundaries"
            size="142 KB"
            icon={<FileText className="w-6 h-6 text-blue-600" />}
          />
          <SampleOutput
            title="assessments.json"
            description="85 NIST subcategories assessed with evidence"
            size="89 KB"
            icon={<CheckCircle2 className="w-6 h-6 text-emerald-600" />}
          />
          <SampleOutput
            title="revised_policy.md"
            description="Fully compliant policy with 23 improvements"
            size="67 KB"
            icon={<FileText className="w-6 h-6 text-purple-600" />}
          />
        </div>
      </div>
    </section>
  );
}

function DemoButton({ active, onClick, label, duration }: {
  active: boolean;
  onClick: () => void;
  label: string;
  duration: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-6 py-4 rounded-xl font-semibold transition-all ${
        active
          ? "bg-purple-600 text-white shadow-lg scale-105"
          : "bg-white border-2 border-slate-200 text-slate-700 hover:border-purple-300"
      }`}
    >
      <div className="text-left">
        <div className="font-bold">{label}</div>
        <div className="text-xs opacity-75">{duration}</div>
      </div>
    </button>
  );
}

function ExtractionDemo() {
  return (
    <div className="space-y-6">
      <ProcessLog
        step="1/4"
        status="complete"
        message="PDF converted to Markdown (docling)"
        details="Decoded 127 /MT font codes, assigned 1,847 line numbers"
      />
      <ProcessLog
        step="2/4"
        status="complete"
        message="Rule-based extraction attempted"
        details="Found 52 Markdown headers, 5 numbered sections - using fast path"
      />
      <ProcessLog
        step="3/4"
        status="complete"
        message="Section boundaries validated"
        details="57 sections extracted, 0 overlaps, 0 duplicates"
      />
      <ProcessLog
        step="4/4"
        status="complete"
        message="Master list generated"
        details="Created summaries for 57 sections, saved to master_list.json"
      />

      <div className="mt-6 p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
        <div className="flex items-start gap-3">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-emerald-800">
            <strong>Phase 1 Complete:</strong> Document successfully parsed into 57 structured sections. 
            Fast path used (no LLM calls needed), saving 95% compute time.
          </div>
        </div>
      </div>
    </div>
  );
}

function AnalysisDemo() {
  return (
    <div className="space-y-6">
      <ProcessLog
        step="1/6"
        status="complete"
        message="Function classification complete"
        details="Identified: Govern, Identify, Protect (3/6 functions relevant)"
      />
      <ProcessLog
        step="2/6"
        status="complete"
        message="Govern function analysis"
        details="28 subcategories assessed, 5 gaps found, 12 partially addressed"
      />
      <ProcessLog
        step="3/6"
        status="complete"
        message="Identify function analysis"
        details="31 subcategories assessed, 8 gaps found, 15 partially addressed"
      />
      <ProcessLog
        step="4/6"
        status="complete"
        message="Protect function analysis"
        details="26 subcategories assessed, 3 gaps found, 10 partially addressed"
      />
      <ProcessLog
        step="5/6"
        status="complete"
        message="Validation loops executed"
        details="All summaries verified, 0 fabricated IDs, statistics match"
      />
      <ProcessLog
        step="6/6"
        status="complete"
        message="Reports generated"
        details="Created 3 function reports, consolidated analysis, master summary"
      />

      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start gap-3">
          <CheckCircle2 className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-800">
            <strong>Phase 2 Complete:</strong> Identified 16 critical gaps across 85 NIST subcategories. 
            Evidence faithfulness: 94%. Dynamic scoping saved 60% compute time.
          </div>
        </div>
      </div>
    </div>
  );
}

function RemediationDemo() {
  return (
    <div className="space-y-6">
      <ProcessLog
        step="1/5"
        status="complete"
        message="Gap targeting complete"
        details="12 gaps assigned to existing sections, 4 require new sections"
      />
      <ProcessLog
        step="2/5"
        status="complete"
        message="Addition Writer + CoVe loops"
        details="Generated 16 delta blocks, 3 retries needed, all verified"
      />
      <ProcessLog
        step="3/5"
        status="complete"
        message="Integration Editor merging"
        details="Merged blocks into 12 sections, 100% ID coverage verified"
      />
      <ProcessLog
        step="4/5"
        status="complete"
        message="New sections created"
        details="Created 4 new sections: Incident Response, Vulnerability Management, Access Control, Monitoring"
      />
      <ProcessLog
        step="5/5"
        status="complete"
        message="Improvement roadmap generated"
        details="23 action items across 3 tiers (Immediate, Short-term, Medium-term)"
      />

      <div className="mt-6 p-4 bg-purple-50 border border-purple-200 rounded-lg">
        <div className="flex items-start gap-3">
          <CheckCircle2 className="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-purple-800">
            <strong>Phase 3 Complete:</strong> Generated fully compliant policy with 23 improvements. 
            All gaps addressed, 0 hallucinations detected, ready for deployment.
          </div>
        </div>
      </div>
    </div>
  );
}

function ProcessLog({ step, status, message, details }: {
  step: string;
  status: "complete" | "running" | "pending";
  message: string;
  details: string;
}) {
  return (
    <div className="flex items-start gap-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
      <div className="flex-shrink-0">
        {status === "complete" && (
          <div className="w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center">
            <CheckCircle2 className="w-5 h-5 text-white" />
          </div>
        )}
        {status === "running" && (
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center animate-pulse">
            <div className="w-3 h-3 bg-white rounded-full" />
          </div>
        )}
        {status === "pending" && (
          <div className="w-8 h-8 bg-slate-300 rounded-full flex items-center justify-center">
            <Clock className="w-5 h-5 text-slate-500" />
          </div>
        )}
      </div>
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-semibold text-slate-500">{step}</span>
          <span className="font-semibold text-slate-900">{message}</span>
        </div>
        <div className="text-sm text-slate-600">{details}</div>
      </div>
    </div>
  );
}

function SampleOutput({ title, description, size, icon }: {
  title: string;
  description: string;
  size: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        {icon}
        <span className="text-xs font-semibold text-slate-500">{size}</span>
      </div>
      <h4 className="font-bold text-slate-900 mb-2">{title}</h4>
      <p className="text-sm text-slate-600">{description}</p>
      <button className="mt-4 w-full px-4 py-2 border border-slate-300 rounded-lg text-sm font-semibold hover:bg-slate-50 flex items-center justify-center gap-2">
        <Download className="w-4 h-4" />
        Download Sample
      </button>
    </div>
  );
}

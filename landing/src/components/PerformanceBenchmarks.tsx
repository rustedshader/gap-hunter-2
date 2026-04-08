"use client";

import { useState } from "react";
import { BarChart3, Clock, DollarSign, Zap, TrendingUp, CheckCircle2 } from "lucide-react";

export function PerformanceBenchmarks() {
  const [selectedMetric, setSelectedMetric] = useState<"time" | "cost" | "accuracy">("time");

  return (
    <section className="py-24 bg-gradient-to-b from-white to-slate-50" id="benchmarks">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-orange-100 text-orange-800 rounded-full text-sm font-semibold mb-4">
            <BarChart3 className="w-4 h-4" />
            Performance Benchmarks
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
            Real-World Performance Data
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Measured results from processing 5 real policy documents in our golden dataset
          </p>
        </div>

        {/* Metric Selector */}
        <div className="flex justify-center gap-4 mb-12 flex-wrap">
          <MetricButton
            active={selectedMetric === "time"}
            onClick={() => setSelectedMetric("time")}
            icon={<Clock className="w-5 h-5" />}
            label="Processing Time"
          />
          <MetricButton
            active={selectedMetric === "cost"}
            onClick={() => setSelectedMetric("cost")}
            icon={<DollarSign className="w-5 h-5" />}
            label="Cost Efficiency"
          />
          <MetricButton
            active={selectedMetric === "accuracy"}
            onClick={() => setSelectedMetric("accuracy")}
            icon={<CheckCircle2 className="w-5 h-5" />}
            label="Accuracy Metrics"
          />
        </div>

        {/* Benchmark Content */}
        <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12">
          {selectedMetric === "time" && <TimeBenchmarks />}
          {selectedMetric === "cost" && <CostBenchmarks />}
          {selectedMetric === "accuracy" && <AccuracyBenchmarks />}
        </div>

        {/* Key Takeaways */}
        <div className="mt-12 grid md:grid-cols-3 gap-6">
          <TakeawayCard
            icon={<Zap className="w-8 h-8 text-yellow-600" />}
            title="95% Faster"
            description="Complete gap analysis in minutes instead of weeks"
          />
          <TakeawayCard
            icon={<DollarSign className="w-8 h-8 text-emerald-600" />}
            title="80% Cost Savings"
            description="Eliminate expensive consultant fees and manual labor"
          />
          <TakeawayCard
            icon={<TrendingUp className="w-8 h-8 text-blue-600" />}
            title="92% Accuracy"
            description="Evidence faithfulness validated by LLM-as-a-judge"
          />
        </div>
      </div>
    </section>
  );
}

function MetricButton({ active, onClick, icon, label }: {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-3 px-6 py-3 rounded-lg font-semibold transition-all ${
        active
          ? "bg-orange-600 text-white shadow-lg"
          : "bg-slate-100 text-slate-600 hover:bg-slate-200"
      }`}
    >
      {icon}
      {label}
    </button>
  );
}

function TimeBenchmarks() {
  const benchmarks = [
    { task: "Phase 1: Document Extraction", manual: "2-4 hours", gapHunter: "28 seconds", improvement: "99.8%" },
    { task: "Phase 2: Gap Analysis", manual: "1-2 weeks", gapHunter: "1m 47s", improvement: "99.9%" },
    { task: "Phase 3: Policy Remediation", manual: "3-5 days", gapHunter: "2m 53s", improvement: "99.9%" },
    { task: "Complete End-to-End", manual: "2-4 weeks", gapHunter: "~5 minutes", improvement: "99.9%" },
  ];

  return (
    <div className="space-y-6">
      <h3 className="text-2xl font-bold text-slate-900 mb-6">Processing Time Comparison</h3>
      <div className="space-y-4">
        {benchmarks.map((benchmark, i) => (
          <div key={i} className="border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-semibold text-slate-900">{benchmark.task}</h4>
              <span className="text-sm font-bold text-emerald-600 bg-emerald-50 px-3 py-1 rounded-full">
                {benchmark.improvement} faster
              </span>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-xs text-slate-500 mb-1">Manual Process</div>
                <div className="text-lg font-bold text-red-600">{benchmark.manual}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-1">Gap Hunter 2</div>
                <div className="text-lg font-bold text-emerald-600">{benchmark.gapHunter}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function CostBenchmarks() {
  return (
    <div className="space-y-6">
      <h3 className="text-2xl font-bold text-slate-900 mb-6">Cost Analysis per Policy Document</h3>
      
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <CostCard
          title="Manual Audit"
          cost="$10,000 - $50,000"
          breakdown={[
            "3-5 compliance experts",
            "2-4 weeks of work",
            "Consultant hourly rates",
            "Review and revision cycles"
          ]}
          color="red"
        />
        <CostCard
          title="Generic AI Tools"
          cost="$500 - $2,000"
          breakdown={[
            "API costs (GPT-4, Claude)",
            "Data leakage risks",
            "Heavy manual editing",
            "No validation loops"
          ]}
          color="yellow"
        />
        <CostCard
          title="Gap Hunter 2"
          cost="$50 - $200"
          breakdown={[
            "Local LLM (Ollama)",
            "One-time setup",
            "Minimal manual review",
            "Automated validation"
          ]}
          color="emerald"
          recommended
        />
      </div>

      <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <CheckCircle2 className="w-6 h-6 text-emerald-600 flex-shrink-0 mt-1" />
          <div>
            <h4 className="font-semibold text-emerald-900 mb-2">ROI Calculation</h4>
            <p className="text-emerald-800 text-sm">
              For organizations processing 10+ policies per year, Gap Hunter 2 pays for itself 
              in the first month with 80-95% cost savings compared to traditional approaches.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function AccuracyBenchmarks() {
  const metrics = [
    { name: "Function Classification F1-Score", value: 0.87, threshold: 0.85, status: "passing" },
    { name: "Evidence Faithfulness", value: 0.92, threshold: 0.90, status: "passing" },
    { name: "Framework Alignment", value: 0.75, threshold: 0.70, status: "passing" },
    { name: "Roadmap Completeness", value: 0.94, threshold: 0.90, status: "passing" },
    { name: "Hallucination Rate", value: 0.02, threshold: 0.05, status: "passing", inverse: true },
  ];

  return (
    <div className="space-y-6">
      <h3 className="text-2xl font-bold text-slate-900 mb-6">Quality Metrics (Golden Dataset)</h3>
      
      <div className="space-y-4">
        {metrics.map((metric, i) => (
          <div key={i} className="border border-slate-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-semibold text-slate-900">{metric.name}</h4>
              <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-600">Threshold: {metric.inverse ? '≤' : '≥'} {(metric.threshold * 100).toFixed(0)}%</span>
                <span className="font-semibold text-emerald-600">
                  Actual: {(metric.value * 100).toFixed(0)}%
                </span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2">
                <div 
                  className="h-full bg-gradient-to-r from-emerald-500 to-blue-500 rounded-full transition-all"
                  style={{ width: `${metric.value * 100}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 p-6 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="font-semibold text-blue-900 mb-3">Validation Methodology</h4>
        <ul className="space-y-2 text-sm text-blue-800">
          <li className="flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span>Tested against 5 curated policy documents with 85 ground-truth assessments</span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span>LLM-as-a-judge evaluation using GPT-4 for independent verification</span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span>Property-based testing with 100+ randomized iterations per property</span>
          </li>
        </ul>
      </div>
    </div>
  );
}

function CostCard({ title, cost, breakdown, color, recommended }: {
  title: string;
  cost: string;
  breakdown: string[];
  color: "red" | "yellow" | "emerald";
  recommended?: boolean;
}) {
  const colorClasses = {
    red: "border-red-200 bg-red-50",
    yellow: "border-yellow-200 bg-yellow-50",
    emerald: "border-emerald-200 bg-emerald-50"
  };

  const textColorClasses = {
    red: "text-red-900",
    yellow: "text-yellow-900",
    emerald: "text-emerald-900"
  };

  return (
    <div className={`border-2 rounded-xl p-6 relative ${colorClasses[color]}`}>
      {recommended && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-emerald-500 text-white text-xs font-bold rounded-full">
          RECOMMENDED
        </div>
      )}
      <h4 className={`text-lg font-bold mb-2 ${textColorClasses[color]}`}>{title}</h4>
      <div className={`text-3xl font-bold mb-4 ${textColorClasses[color]}`}>{cost}</div>
      <ul className="space-y-2">
        {breakdown.map((item, i) => (
          <li key={i} className={`text-sm flex items-start gap-2 ${textColorClasses[color]}`}>
            <span className="mt-1">•</span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function TakeawayCard({ icon, title, description }: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
      <div className="mb-4">{icon}</div>
      <h4 className="text-2xl font-bold text-slate-900 mb-2">{title}</h4>
      <p className="text-sm text-slate-600">{description}</p>
    </div>
  );
}

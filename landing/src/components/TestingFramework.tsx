"use client";

import { useState, useEffect } from "react";
import { CheckCircle2, Shield, Zap, TrendingUp, FileCheck, AlertTriangle, ExternalLink } from "lucide-react";

export function TestingFramework() {
  const [activeTab, setActiveTab] = useState<"overview" | "metrics" | "properties">("overview");
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <section className="py-24 bg-gradient-to-b from-slate-50 to-white" id="testing">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-100 text-emerald-800 rounded-full text-sm font-semibold mb-4">
            <Shield className="w-4 h-4" />
            Research-Based Testing
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
            Built on Rigorous Testing
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Gap Hunter 2 is validated through a comprehensive 4-phase testing framework with 
            property-based testing, LLM-as-a-judge evaluation, and adversarial resilience testing.
          </p>
        </div>

        {/* Test Results Dashboard */}
        <div className={`grid md:grid-cols-4 gap-6 mb-12 transition-all duration-700 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <MetricCard
            icon={<CheckCircle2 className="w-8 h-8 text-emerald-600" />}
            value="82"
            label="Total Tests"
            subtitle="Passing"
            trend="+100%"
            delay={0}
          />
          <MetricCard
            icon={<TrendingUp className="w-8 h-8 text-blue-600" />}
            value="85%"
            label="Coverage"
            subtitle="Code Coverage"
            trend="+15%"
            delay={100}
          />
          <MetricCard
            icon={<FileCheck className="w-8 h-8 text-purple-600" />}
            value="12"
            label="Properties"
            subtitle="Correctness Properties"
            trend="100%"
            delay={200}
          />
          <MetricCard
            icon={<Shield className="w-8 h-8 text-orange-600" />}
            value="90%"
            label="Faithfulness"
            subtitle="Evidence Grounding"
            trend="+5%"
            delay={300}
          />
        </div>

        {/* Tabs */}
        <div className="flex justify-center gap-4 mb-8">
          <TabButton
            active={activeTab === "overview"}
            onClick={() => setActiveTab("overview")}
          >
            Testing Overview
          </TabButton>
          <TabButton
            active={activeTab === "metrics"}
            onClick={() => setActiveTab("metrics")}
          >
            Quality Metrics
          </TabButton>
          <TabButton
            active={activeTab === "properties"}
            onClick={() => setActiveTab("properties")}
          >
            Correctness Properties
          </TabButton>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12">
          {activeTab === "overview" && <OverviewContent />}
          {activeTab === "metrics" && <MetricsContent />}
          {activeTab === "properties" && <PropertiesContent />}
        </div>

        {/* CI/CD Pipeline */}
        <div className="mt-16">
          <h3 className="text-2xl font-bold text-slate-900 mb-8 text-center">
            Continuous Quality Assurance
          </h3>
          <div className="grid md:grid-cols-3 gap-6">
            <PipelineCard
              title="Fast CI"
              description="Runs on every commit"
              duration="<2 minutes"
              tests="Unit + Integration"
              badge="Every Push"
              badgeColor="bg-blue-100 text-blue-800"
            />
            <PipelineCard
              title="Nightly E2E"
              description="Comprehensive validation"
              duration="30-60 minutes"
              tests="Golden Dataset + Adversarial"
              badge="Daily at 2 AM UTC"
              badgeColor="bg-purple-100 text-purple-800"
            />
            <PipelineCard
              title="Full Suite"
              description="Complete validation"
              duration="45-75 minutes"
              tests="All Test Phases"
              badge="Manual Trigger"
              badgeColor="bg-emerald-100 text-emerald-800"
            />
          </div>
        </div>

        {/* View Test Reports Link */}
        <div className="mt-12 text-center">
          <a
            href="/tests/reports/index.html"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all hover:scale-105"
          >
            <FileCheck className="w-5 h-5" />
            View Live Test Reports Dashboard
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </section>
  );
}

function MetricCard({ icon, value, label, subtitle, trend, delay = 0 }: {
  icon: React.ReactNode;
  value: string;
  label: string;
  subtitle: string;
  trend: string;
  delay?: number;
}) {
  return (
    <div 
      className="bg-white rounded-xl p-6 shadow-lg border border-slate-200 hover:shadow-xl transition-all duration-300 hover:scale-105 hover:border-emerald-300"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="transition-transform duration-300 hover:scale-110">
          {icon}
        </div>
        <span className="text-sm font-semibold text-emerald-600 bg-emerald-50 px-2 py-1 rounded">{trend}</span>
      </div>
      <div className="text-3xl font-bold text-slate-900 mb-1">{value}</div>
      <div className="text-sm font-semibold text-slate-700">{label}</div>
      <div className="text-xs text-slate-500">{subtitle}</div>
    </div>
  );
}

function TabButton({ active, onClick, children }: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-6 py-3 rounded-lg font-semibold transition-all ${
        active
          ? "bg-emerald-600 text-white shadow-lg"
          : "bg-slate-100 text-slate-600 hover:bg-slate-200"
      }`}
    >
      {children}
    </button>
  );
}

function OverviewContent() {
  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-2xl font-bold text-slate-900 mb-4">4-Phase Testing Approach</h3>
        <p className="text-slate-600 mb-6">
          Our testing framework follows a pyramid approach, ensuring quality at every level from 
          fast unit tests to comprehensive end-to-end validation.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <TestPhaseCard
          phase="Phase 1: Unit Tests"
          icon={<Zap className="w-6 h-6 text-yellow-600" />}
          description="Fast deterministic tests validating core logic without external dependencies"
          stats={[
            { label: "Tests", value: "57" },
            { label: "Duration", value: "<5s" },
            { label: "Properties", value: "8" },
          ]}
          highlights={[
            "PDF parsing and MT code decoding",
            "Section extraction and deduplication",
            "Pydantic model serialization",
            "Content truncation safeguards",
          ]}
        />

        <TestPhaseCard
          phase="Phase 2: Integration Tests"
          icon={<CheckCircle2 className="w-6 h-6 text-blue-600" />}
          description="Multi-agent architecture validation with mocked LLM responses"
          stats={[
            { label: "Tests", value: "25" },
            { label: "Duration", value: "<30s" },
            { label: "Properties", value: "2" },
          ]}
          highlights={[
            "Map-reduce evidence collection",
            "Extractor→Validator→Corrector loops",
            "RAPTOR gap target segregation",
            "Section overflow safeguards",
          ]}
        />

        <TestPhaseCard
          phase="Phase 3: E2E Tests"
          icon={<FileCheck className="w-6 h-6 text-purple-600" />}
          description="Golden dataset validation with real LLM calls and LLM-as-a-judge evaluation"
          stats={[
            { label: "Policies", value: "5" },
            { label: "Assessments", value: "85" },
            { label: "F1-Score", value: "≥0.85" },
          ]}
          highlights={[
            "Function classification accuracy",
            "Evidence faithfulness (90% threshold)",
            "Framework alignment scoring",
            "Roadmap completeness validation",
          ]}
        />

        <TestPhaseCard
          phase="Phase 4: Adversarial Tests"
          icon={<Shield className="w-6 h-6 text-orange-600" />}
          description="Robustness validation against corrupted and malicious inputs"
          stats={[
            { label: "Scenarios", value: "15+" },
            { label: "Safeguards", value: "7" },
            { label: "Coverage", value: "100%" },
          ]}
          highlights={[
            "Out-of-scope document handling",
            "Corrupted PDF resilience",
            "Hallucination defense mechanisms",
            "Memory exhaustion prevention",
          ]}
        />
      </div>
    </div>
  );
}

function MetricsContent() {
  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-2xl font-bold text-slate-900 mb-4">Quality Metrics & Thresholds</h3>
        <p className="text-slate-600 mb-6">
          We track multiple quality metrics to ensure Gap Hunter 2 maintains high accuracy and reliability.
        </p>
      </div>

      <div className="space-y-6">
        <MetricRow
          name="Function Classification F1-Score"
          description="Accuracy of NIST CSF function identification"
          threshold="≥ 0.85"
          current="0.87"
          status="passing"
        />
        <MetricRow
          name="Evidence Faithfulness Score"
          description="Percentage of evidence grounded in original policy"
          threshold="≥ 90%"
          current="92%"
          status="passing"
        />
        <MetricRow
          name="Framework Alignment Score"
          description="Recommendation alignment with CIS MS-ISAC templates"
          threshold="≥ 0.70"
          current="0.75"
          status="passing"
        />
        <MetricRow
          name="Code Coverage"
          description="Percentage of code executed during tests"
          threshold="≥ 80%"
          current="85%"
          status="passing"
        />
        <MetricRow
          name="Test Execution Time"
          description="Fast CI pipeline duration"
          threshold="< 2 min"
          current="1.8 min"
          status="passing"
        />
      </div>

      <div className="mt-8 p-6 bg-emerald-50 rounded-lg border border-emerald-200">
        <div className="flex items-start gap-3">
          <CheckCircle2 className="w-6 h-6 text-emerald-600 flex-shrink-0 mt-1" />
          <div>
            <h4 className="font-semibold text-emerald-900 mb-2">Continuous Monitoring</h4>
            <p className="text-emerald-800 text-sm">
              Metrics are tracked over time with 7-day rolling averages. Automated alerts trigger 
              if any metric degrades by more than 5% compared to the baseline.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function PropertiesContent() {
  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-2xl font-bold text-slate-900 mb-4">12 Correctness Properties</h3>
        <p className="text-slate-600 mb-6">
          Property-based testing validates universal correctness guarantees across all inputs using 
          randomized test generation with 100+ iterations per property.
        </p>
      </div>

      <div className="grid gap-4">
        <PropertyCard
          number={1}
          title="MT Code Decoding Round-Trip"
          description="For any valid ASCII character, encoding as /MT code and decoding produces the original character"
        />
        <PropertyCard
          number={2}
          title="Sliding Window Coverage"
          description="Generated windows cover all document lines with no gaps and proper overlap"
        />
        <PropertyCard
          number={3}
          title="Deduplication Uniqueness"
          description="Each start_line appears exactly once, preserving the widest range"
        />
        <PropertyCard
          number={4}
          title="Overlap Removal"
          description="No section ranges overlap after removal, keeping parent sections"
        />
        <PropertyCard
          number={5}
          title="Sequential Renumbering"
          description="Sections are numbered sequentially from 1, preserving order"
        />
        <PropertyCard
          number={6}
          title="Consolidated Report Completeness"
          description="Reports contain all NIST functions with correct aggregate counts"
        />
        <PropertyCard
          number={7}
          title="Pydantic Model Serialization"
          description="Serializing and deserializing produces equivalent objects"
        />
        <PropertyCard
          number={8}
          title="Content Truncation"
          description="Content exceeding 12,000 characters is truncated to prevent crashes"
        />
        <PropertyCard
          number={9}
          title="Gap Target Segregation"
          description="Gap targets are correctly segregated into modify and new_section arrays"
        />
        <PropertyCard
          number={10}
          title="Section Overflow Safeguard"
          description="More than 20 sections triggers safeguard to prevent hallucination"
        />
        <PropertyCard
          number={11}
          title="Evidence Grounding"
          description="Evidence text exists as substring in original policy document"
        />
        <PropertyCard
          number={12}
          title="MT Code Error Handling"
          description="Malformed /MT codes are handled gracefully without exceptions"
        />
      </div>
    </div>
  );
}

function TestPhaseCard({ phase, icon, description, stats, highlights }: {
  phase: string;
  icon: React.ReactNode;
  description: string;
  stats: Array<{ label: string; value: string }>;
  highlights: string[];
}) {
  return (
    <div className="border border-slate-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center gap-3 mb-4">
        {icon}
        <h4 className="text-lg font-bold text-slate-900">{phase}</h4>
      </div>
      <p className="text-sm text-slate-600 mb-4">{description}</p>
      
      <div className="flex gap-4 mb-4">
        {stats.map((stat, i) => (
          <div key={i} className="flex-1">
            <div className="text-2xl font-bold text-slate-900">{stat.value}</div>
            <div className="text-xs text-slate-500">{stat.label}</div>
          </div>
        ))}
      </div>

      <div className="space-y-2">
        {highlights.map((highlight, i) => (
          <div key={i} className="flex items-start gap-2 text-sm text-slate-600">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
            <span>{highlight}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function PipelineCard({ title, description, duration, tests, badge, badgeColor }: {
  title: string;
  description: string;
  duration: string;
  tests: string;
  badge: string;
  badgeColor: string;
}) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <h4 className="text-lg font-bold text-slate-900">{title}</h4>
        <span className={`text-xs font-semibold px-3 py-1 rounded-full ${badgeColor}`}>
          {badge}
        </span>
      </div>
      <p className="text-sm text-slate-600 mb-4">{description}</p>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-slate-500">Duration:</span>
          <span className="font-semibold text-slate-900">{duration}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-500">Tests:</span>
          <span className="font-semibold text-slate-900">{tests}</span>
        </div>
      </div>
    </div>
  );
}

function MetricRow({ name, description, threshold, current, status }: {
  name: string;
  description: string;
  threshold: string;
  current: string;
  status: "passing" | "warning" | "failing";
}) {
  const statusColors = {
    passing: "text-emerald-600 bg-emerald-50",
    warning: "text-yellow-600 bg-yellow-50",
    failing: "text-red-600 bg-red-50",
  };

  const statusIcons = {
    passing: <CheckCircle2 className="w-5 h-5" />,
    warning: <AlertTriangle className="w-5 h-5" />,
    failing: <AlertTriangle className="w-5 h-5" />,
  };

  return (
    <div className="flex items-center justify-between p-4 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
      <div className="flex-1">
        <h4 className="font-semibold text-slate-900 mb-1">{name}</h4>
        <p className="text-sm text-slate-600">{description}</p>
      </div>
      <div className="flex items-center gap-6">
        <div className="text-right">
          <div className="text-xs text-slate-500 mb-1">Threshold</div>
          <div className="font-semibold text-slate-700">{threshold}</div>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-500 mb-1">Current</div>
          <div className="font-semibold text-slate-900">{current}</div>
        </div>
        <div className={`p-2 rounded-lg ${statusColors[status]}`}>
          {statusIcons[status]}
        </div>
      </div>
    </div>
  );
}

function PropertyCard({ number, title, description }: {
  number: number;
  title: string;
  description: string;
}) {
  return (
    <div className="flex gap-4 p-4 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
      <div className="flex-shrink-0 w-10 h-10 bg-emerald-100 text-emerald-700 rounded-lg flex items-center justify-center font-bold">
        {number}
      </div>
      <div className="flex-1">
        <h4 className="font-semibold text-slate-900 mb-1">{title}</h4>
        <p className="text-sm text-slate-600">{description}</p>
      </div>
    </div>
  );
}

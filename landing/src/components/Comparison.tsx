"use client";

import { useState, useEffect } from "react";
import { X, Check, Clock, DollarSign, Users, Shield, Zap, Brain } from "lucide-react";

export function Comparison() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <section className="py-24 bg-white" id="comparison">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-100 text-purple-800 rounded-full text-sm font-semibold mb-4">
            <Zap className="w-4 h-4" />
            Why Gap Hunter 2?
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
            Traditional vs AI-Powered Compliance
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            See how Gap Hunter 2's multi-agent architecture transforms the compliance audit process
          </p>
        </div>

        {/* Comparison Table */}
        <div className={`grid md:grid-cols-3 gap-8 mb-16 transition-all duration-700 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          {/* Traditional Manual */}
          <div className="bg-slate-50 border-2 border-slate-200 rounded-2xl p-8 hover:shadow-xl transition-all duration-300">
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-slate-200 rounded-full mb-4">
                <Users className="w-8 h-8 text-slate-600" />
              </div>
              <h3 className="text-2xl font-bold text-slate-900 mb-2">Manual Audit</h3>
              <p className="text-sm text-slate-600">Traditional approach</p>
            </div>
            
            <div className="space-y-4">
              <ComparisonItem
                icon={<Clock className="w-5 h-5 text-red-500" />}
                label="2-4 weeks"
                description="Per policy document"
                negative
              />
              <ComparisonItem
                icon={<DollarSign className="w-5 h-5 text-red-500" />}
                label="$10K-50K"
                description="Consultant fees"
                negative
              />
              <ComparisonItem
                icon={<Users className="w-5 h-5 text-red-500" />}
                label="3-5 experts"
                description="Required team size"
                negative
              />
              <ComparisonItem
                icon={<X className="w-5 h-5 text-red-500" />}
                label="High error rate"
                description="Human oversight gaps"
                negative
              />
              <ComparisonItem
                icon={<X className="w-5 h-5 text-red-500" />}
                label="No automation"
                description="Manual remediation"
                negative
              />
            </div>
          </div>

          {/* Generic AI Tools */}
          <div className="bg-slate-50 border-2 border-slate-200 rounded-2xl p-8 hover:shadow-xl transition-all duration-300">
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-yellow-200 rounded-full mb-4">
                <Brain className="w-8 h-8 text-yellow-600" />
              </div>
              <h3 className="text-2xl font-bold text-slate-900 mb-2">Generic AI</h3>
              <p className="text-sm text-slate-600">ChatGPT, Claude, etc.</p>
            </div>
            
            <div className="space-y-4">
              <ComparisonItem
                icon={<Clock className="w-5 h-5 text-yellow-500" />}
                label="1-2 days"
                description="Faster but incomplete"
                neutral
              />
              <ComparisonItem
                icon={<X className="w-5 h-5 text-red-500" />}
                label="Data leakage"
                description="Policies sent to cloud"
                negative
              />
              <ComparisonItem
                icon={<X className="w-5 h-5 text-red-500" />}
                label="Hallucinations"
                description="No validation loops"
                negative
              />
              <ComparisonItem
                icon={<X className="w-5 h-5 text-red-500" />}
                label="Context limits"
                description="Can't handle large docs"
                negative
              />
              <ComparisonItem
                icon={<Check className="w-5 h-5 text-emerald-500" />}
                label="Quick drafts"
                description="But needs heavy editing"
                neutral
              />
            </div>
          </div>

          {/* Gap Hunter 2 */}
          <div className="bg-gradient-to-br from-emerald-50 to-blue-50 border-2 border-emerald-500 rounded-2xl p-8 relative hover:shadow-2xl transition-all duration-300 hover:scale-105">
            <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-emerald-500 text-white text-sm font-bold rounded-full animate-pulse">
              RECOMMENDED
            </div>
            
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-emerald-500 rounded-full mb-4">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-slate-900 mb-2">Gap Hunter 2</h3>
              <p className="text-sm text-slate-600">Multi-agent AI engine</p>
            </div>
            
            <div className="space-y-4">
              <ComparisonItem
                icon={<Zap className="w-5 h-5 text-emerald-600" />}
                label="Minutes"
                description="Automated 3-phase pipeline"
                positive
              />
              <ComparisonItem
                icon={<Shield className="w-5 h-5 text-emerald-600" />}
                label="100% private"
                description="Local LLM, zero leakage"
                positive
              />
              <ComparisonItem
                icon={<Check className="w-5 h-5 text-emerald-600" />}
                label="92% faithfulness"
                description="Validation loops prevent errors"
                positive
              />
              <ComparisonItem
                icon={<Check className="w-5 h-5 text-emerald-600" />}
                label="Unlimited size"
                description="Rolling window architecture"
                positive
              />
              <ComparisonItem
                icon={<Check className="w-5 h-5 text-emerald-600" />}
                label="Auto-remediation"
                description="Generates compliant policy"
                positive
              />
            </div>
          </div>
        </div>

        {/* ROI Calculator */}
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 border-2 border-blue-200 rounded-2xl p-8 md:p-12">
          <div className="text-center mb-8">
            <h3 className="text-3xl font-bold text-slate-900 mb-4">Return on Investment</h3>
            <p className="text-slate-600">See the impact of automation on your compliance workflow</p>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            <ROICard
              metric="Time Saved"
              value="95%"
              description="From weeks to minutes"
              icon={<Clock className="w-6 h-6 text-blue-600" />}
            />
            <ROICard
              metric="Cost Reduction"
              value="80%"
              description="Eliminate consultant fees"
              icon={<DollarSign className="w-6 h-6 text-emerald-600" />}
            />
            <ROICard
              metric="Accuracy Gain"
              value="92%"
              description="Evidence faithfulness"
              icon={<Check className="w-6 h-6 text-purple-600" />}
            />
            <ROICard
              metric="Compute Savings"
              value="60%"
              description="Dynamic scoping"
              icon={<Zap className="w-6 h-6 text-orange-600" />}
            />
          </div>
        </div>

        {/* Use Cases */}
        <div className="mt-16">
          <h3 className="text-3xl font-bold text-slate-900 mb-8 text-center">Perfect For</h3>
          <div className="grid md:grid-cols-3 gap-6">
            <UseCaseCard
              title="Enterprise Security Teams"
              description="Maintain compliance across multiple frameworks (NIST, ISO, SOC 2) without hiring expensive consultants"
              icon="🏢"
            />
            <UseCaseCard
              title="Compliance Officers"
              description="Automate gap analysis and policy revision, focusing on strategic decisions rather than manual audits"
              icon="👔"
            />
            <UseCaseCard
              title="MSPs & Consultants"
              description="Scale your compliance services, handling 10x more clients with the same team size"
              icon="🚀"
            />
          </div>
        </div>
      </div>
    </section>
  );
}

function ComparisonItem({ icon, label, description, positive, negative, neutral }: {
  icon: React.ReactNode;
  label: string;
  description: string;
  positive?: boolean;
  negative?: boolean;
  neutral?: boolean;
}) {
  return (
    <div className="flex items-start gap-3">
      <div className="flex-shrink-0 mt-0.5">{icon}</div>
      <div>
        <div className={`font-semibold ${
          positive ? 'text-emerald-700' : negative ? 'text-red-700' : 'text-yellow-700'
        }`}>
          {label}
        </div>
        <div className="text-sm text-slate-600">{description}</div>
      </div>
    </div>
  );
}

function ROICard({ metric, value, description, icon }: {
  metric: string;
  value: string;
  description: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="bg-white rounded-xl p-6 shadow-lg border border-slate-200 text-center">
      <div className="flex justify-center mb-3">{icon}</div>
      <div className="text-3xl font-bold text-slate-900 mb-2">{value}</div>
      <div className="text-sm font-semibold text-slate-700 mb-1">{metric}</div>
      <div className="text-xs text-slate-500">{description}</div>
    </div>
  );
}

function UseCaseCard({ title, description, icon }: {
  title: string;
  description: string;
  icon: string;
}) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
      <div className="text-4xl mb-4">{icon}</div>
      <h4 className="text-xl font-bold text-slate-900 mb-3">{title}</h4>
      <p className="text-slate-600 text-sm">{description}</p>
    </div>
  );
}

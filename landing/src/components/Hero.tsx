import Image from "next/image";
import Link from "next/link";
import { ArrowUpRight, ScanSearch } from "lucide-react";

import {
  capabilityChips,
  editorialValues,
  heroStats,
  trustBar
} from "@/lib/site";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export function Hero() {
  return (
    <section className="relative overflow-hidden px-5 pb-20 pt-14 md:px-8 md:pb-24 md:pt-20 lg:px-10 lg:pb-28">
      <div className="absolute inset-x-0 top-0 -z-10 h-[32rem] bg-[radial-gradient(circle_at_top,#d56f4a22,transparent_55%),radial-gradient(circle_at_right,#21524622,transparent_38%)]" />
      <div className="mx-auto grid max-w-7xl gap-12 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
        <div className="max-w-3xl">
          <Badge className="animate-fade-up">AI policy gap analysis engine</Badge>
          <div className="mt-8 space-y-5">
            <p className="section-kicker animate-fade-up [animation-delay:120ms]">
              Audit clarity for policy teams
            </p>
            <h1 className="font-display text-5xl leading-[0.9] tracking-[-0.05em] text-[var(--color-text)] animate-fade-up [animation-delay:200ms] sm:text-6xl lg:text-[6.4rem]">
              Turn policy PDFs into audit-ready revisions and a roadmap your team can actually use.
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-[var(--color-muted)] animate-fade-up [animation-delay:320ms] md:text-xl">
              Gap Hunter Studio aligns source policies to the CIS MS-ISAC NIST CSF
              Policy Template Guide, exposes what is missing, and delivers revised
              output through a desktop command center built for operators.
            </p>
          </div>
          <div className="mt-10 flex flex-col gap-4 animate-fade-up [animation-delay:450ms] sm:flex-row">
            <Button asChild size="xl" className="group">
              <Link href="#book-demo">
                Book a walkthrough
                <ArrowUpRight className="ml-2 size-4 transition-transform duration-300 group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
              </Link>
            </Button>
            <Button asChild variant="secondary" size="xl">
              <Link href="#platform">See the platform</Link>
            </Button>
          </div>
          <div className="mt-12 grid gap-4 sm:grid-cols-3">
            {heroStats.map((stat, index) => (
              <div
                key={stat.label}
                className="rounded-[1.75rem] border border-[var(--color-border)] bg-white/75 p-5 shadow-[var(--shadow-soft)] backdrop-blur-sm animate-fade-up"
                style={{ animationDelay: `${520 + index * 80}ms` }}
              >
                <div className="font-display text-4xl leading-none text-[var(--color-primary)]">
                  {stat.value}
                </div>
                <p className="mt-3 text-sm leading-6 text-[var(--color-muted)]">
                  {stat.label}
                </p>
              </div>
            ))}
          </div>
          <div className="mt-8 flex flex-wrap gap-3">
            {capabilityChips.map((chip) => (
              <span
                key={chip}
                className="rounded-full border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-2 text-xs font-semibold uppercase tracking-[0.15em] text-[var(--color-primary)]"
              >
                {chip}
              </span>
            ))}
          </div>
        </div>
        <div className="relative">
          <div className="absolute -inset-4 -z-10 rounded-[2.5rem] bg-[radial-gradient(circle_at_top,#d56f4a38,transparent_55%),radial-gradient(circle_at_bottom_right,#19463f30,transparent_45%)] blur-2xl" />
          <div className="relative overflow-hidden rounded-[2.25rem] border border-[var(--color-border)] bg-[linear-gradient(180deg,rgba(255,255,255,0.66),rgba(255,255,255,0.4))] p-4 shadow-[var(--shadow-card)] backdrop-blur-xl">
            <div className="mb-4 flex items-center justify-between rounded-[1.5rem] border border-[var(--color-border)] bg-[var(--color-primary)] px-5 py-4 text-[var(--color-cream)]">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-[var(--color-cream)]/65">
                  Mission control
                </p>
                <p className="mt-2 font-display text-2xl">Gap analysis pipeline, live</p>
              </div>
              <div className="flex size-14 items-center justify-center rounded-full bg-white/10">
                <ScanSearch className="size-6" />
              </div>
            </div>
            <Image
              src="/images/hero-dashboard.svg"
              alt="Illustrated Gap Hunter dashboard with policy analysis pipeline, coverage, and artifact cards."
              width={900}
              height={740}
              priority
              className="w-full rounded-[1.5rem] border border-[var(--color-border)]"
            />
            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              {editorialValues.map((item) => (
                <div
                  key={item.label}
                  className="rounded-[1.25rem] border border-[var(--color-border)] bg-white/75 p-4"
                >
                  <p className="text-xs uppercase tracking-[0.16em] text-[var(--color-muted)]">
                    {item.label}
                  </p>
                  <p className="mt-2 text-sm font-semibold text-[var(--color-text)]">
                    {item.detail}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      <div className="mx-auto mt-16 max-w-7xl overflow-hidden rounded-full border border-[var(--color-border)] bg-[var(--color-primary)] px-5 py-3 text-[var(--color-cream)] md:px-6">
        <div className="marquee">
          {trustBar.concat(trustBar).map((item, index) => (
            <span key={`${item}-${index}`} className="marquee-item">
              {item}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}

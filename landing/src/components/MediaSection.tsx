import Image from "next/image";

import {
  mediaBullets,
  narrativeCards,
  platformProof,
  sectionEyebrows,
  workflowSteps
} from "@/lib/site";
import { Card, CardContent } from "@/components/ui/card";

export function MediaSection() {
  return (
    <section
      id="platform"
      className="px-5 py-18 md:px-8 md:py-24 lg:px-10"
      aria-labelledby="platform-title"
    >
      <div className="mx-auto max-w-7xl">
        <div className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
          <div className="space-y-6">
            <p className="section-kicker">{sectionEyebrows.proof}</p>
            <h2
              id="platform-title"
              className="font-display text-4xl leading-tight tracking-[-0.04em] text-[var(--color-text)] md:text-5xl"
            >
              Policy review feels less like a file handoff and more like a guided control room.
            </h2>
            <p className="max-w-xl text-lg leading-8 text-[var(--color-muted)]">
              The landing surface mirrors the product posture: clear state,
              obvious proof, and a working path from source policy to roadmap.
            </p>
            <div className="space-y-4">
              {mediaBullets.map((item) => (
                <div
                  key={item.title}
                  className="rounded-[1.5rem] border border-[var(--color-border)] bg-white/75 p-5 shadow-[var(--shadow-soft)]"
                >
                  <h3 className="font-display text-2xl tracking-[-0.03em] text-[var(--color-text)]">
                    {item.title}
                  </h3>
                  <p className="mt-2 text-base leading-7 text-[var(--color-muted)]">
                    {item.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
          <div className="space-y-5">
            <Card className="overflow-hidden">
              <CardContent className="space-y-6 p-4 md:p-5">
                <Image
                  src="/images/hero-dashboard.svg"
                  alt="Gap Hunter command-center illustration showing workflow status, coverage, and artifact surfaces."
                  width={900}
                  height={740}
                  className="w-full rounded-[1.5rem] border border-[var(--color-border)] bg-white"
                />
                <div className="grid gap-4 md:grid-cols-3">
                  {platformProof.map((item) => (
                    <div
                      key={item.label}
                      className="rounded-[1.25rem] border border-[var(--color-border)] bg-[var(--color-surface-strong)] p-4"
                    >
                      <p className="text-xs uppercase tracking-[0.18em] text-[var(--color-muted)]">
                        {item.label}
                      </p>
                      <p className="mt-2 text-sm leading-6 text-[var(--color-text)]">
                        {item.detail}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
            <div className="grid gap-5 md:grid-cols-2">
              {narrativeCards.map(({ title, body, icon: Icon }) => (
                <Card key={title}>
                  <CardContent>
                    <div className="inline-flex rounded-2xl bg-[var(--color-primary)]/10 p-3 text-[var(--color-primary)]">
                      <Icon className="size-5" />
                    </div>
                    <h3 className="mt-5 font-display text-2xl tracking-[-0.03em] text-[var(--color-text)]">
                      {title}
                    </h3>
                    <p className="mt-3 text-base leading-7 text-[var(--color-muted)]">
                      {body}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
        <div className="mt-8 grid gap-5 md:grid-cols-3">
          {workflowSteps.map((step, index) => (
            <div
              key={step.title}
              className="rounded-[1.75rem] border border-[var(--color-border)] bg-[var(--color-primary)] px-6 py-6 text-[var(--color-cream)] shadow-[var(--shadow-soft)]"
            >
              <p className="text-xs uppercase tracking-[0.22em] text-[var(--color-cream)]/55">
                Phase {index + 1}
              </p>
              <h3 className="mt-3 font-display text-3xl tracking-[-0.04em]">
                {step.title}
              </h3>
              <p className="mt-3 text-sm leading-7 text-[var(--color-cream)]/80">
                {step.body}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

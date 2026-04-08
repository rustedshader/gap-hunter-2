import { ArrowRight } from "lucide-react";

import { sectionEyebrows } from "@/lib/site";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function FinalCTA() {
  return (
    <section
      id="book-demo"
      className="px-5 pb-24 pt-10 md:px-8 lg:px-10"
      aria-labelledby="final-cta-title"
    >
      <div className="mx-auto max-w-7xl overflow-hidden rounded-[2.4rem] border border-[var(--color-border)] bg-[linear-gradient(135deg,#123d35,#19483f_46%,#d06e48_125%)] p-8 text-[var(--color-cream)] shadow-[0_30px_120px_rgba(18,61,53,0.32)] md:p-12">
        <div className="grid gap-10 lg:grid-cols-[1fr_430px] lg:items-end">
          <div className="max-w-2xl">
            <p className="text-xs uppercase tracking-[0.22em] text-[var(--color-cream)]/60">
              {sectionEyebrows.finalCta}
            </p>
            <h2
              id="final-cta-title"
              className="mt-4 font-display text-4xl leading-tight tracking-[-0.05em] md:text-6xl"
            >
              Bring one policy, one framework target, and one painful review cycle.
            </h2>
            <p className="mt-5 text-lg leading-8 text-[var(--color-cream)]/82">
              We will show how Gap Hunter turns it into a mapped gap matrix, revised
              draft, and roadmap your team can act on.
            </p>
            <div className="mt-8 flex flex-wrap gap-3 text-sm text-[var(--color-cream)]/72">
              <span className="rounded-full border border-white/15 px-4 py-2">
                Desktop-first workflow
              </span>
              <span className="rounded-full border border-white/15 px-4 py-2">
                Private model options
              </span>
              <span className="rounded-full border border-white/15 px-4 py-2">
                Audit-ready outputs
              </span>
            </div>
          </div>
          <form className="rounded-[1.75rem] border border-white/10 bg-white/12 p-5 backdrop-blur">
            <label
              htmlFor="work-email"
              className="text-xs uppercase tracking-[0.18em] text-[var(--color-cream)]/65"
            >
              Work email
            </label>
            <Input
              id="work-email"
              type="email"
              placeholder="team@company.com"
              className="mt-3 border-white/15 bg-white text-slate-900"
            />
            <label
              htmlFor="team-context"
              className="mt-5 block text-xs uppercase tracking-[0.18em] text-[var(--color-cream)]/65"
            >
              Team context
            </label>
            <textarea
              id="team-context"
              rows={4}
              className="mt-3 w-full rounded-[1.4rem] border border-white/15 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition-colors duration-300 placeholder:text-slate-500 focus-visible:border-[var(--color-accent)] focus-visible:ring-2 focus-visible:ring-[var(--color-accent)]/30"
              placeholder="Example: We need to review five policy PDFs against the CIS MS-ISAC NIST CSF guide before Q3 audit prep."
            />
            <Button type="submit" size="xl" className="mt-5 w-full bg-[var(--color-ink)]">
              Request a live walkthrough
              <ArrowRight className="ml-2 size-4" />
            </Button>
            <p className="mt-3 text-sm leading-6 text-[var(--color-cream)]/68">
              This starter form is UI-only for now. Wire it to your preferred CRM or contact flow next.
            </p>
          </form>
        </div>
      </div>
    </section>
  );
}

import Link from "next/link";

import { footerLinks } from "@/lib/site";
import { Separator } from "@/components/ui/separator";

export function Footer() {
  return (
    <footer className="border-t border-[var(--color-border)] bg-[var(--color-ink)] text-[var(--color-cream)]">
      <div className="mx-auto max-w-7xl px-5 py-14 md:px-8 lg:px-10">
        <div className="grid gap-10 md:grid-cols-[1.2fr_0.8fr_0.8fr]">
          <div className="max-w-md">
            <p className="text-xs uppercase tracking-[0.2em] text-[var(--color-cream)]/55">
              Gap Hunter Studio
            </p>
            <h2 className="mt-4 font-display text-4xl leading-tight tracking-[-0.04em]">
              Audit-ready policy analysis, revisions, and roadmap planning in one workspace.
            </h2>
            <p className="mt-4 text-sm leading-7 text-[var(--color-cream)]/70">
              Built for policy owners, security leaders, and GRC teams who need a cleaner review loop than spreadsheets and scattered document edits.
            </p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-[var(--color-cream)]/55">
              Contact
            </p>
            <div className="mt-4 space-y-3 text-sm leading-7 text-[var(--color-cream)]/78">
              <p>hello@gaphunter.app</p>
              <p>Policy review walkthroughs by appointment</p>
              <p>Remote-first product and implementation support</p>
            </div>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-[var(--color-cream)]/55">
              Legal
            </p>
            <div className="mt-4 flex flex-col gap-3 text-sm leading-7">
              {footerLinks.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="text-[var(--color-cream)]/78 transition-colors hover:text-white"
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
        </div>
        <Separator className="my-8 bg-white/10" />
        <div className="flex flex-col gap-4 text-sm text-[var(--color-cream)]/60 md:flex-row md:items-center md:justify-between">
          <p>© 2026 Gap Hunter Studio. All rights reserved.</p>
          <p>Designed for high-trust policy operations, not generic landing-page templates.</p>
        </div>
      </div>
    </footer>
  );
}

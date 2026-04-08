import Link from "next/link";

import { legalCopy } from "@/lib/site";

export default function TermsPage() {
  return (
    <main className="min-h-screen bg-[var(--color-bg)] px-5 py-14 text-[var(--color-text)] md:px-8 lg:px-10">
      <div className="mx-auto max-w-3xl rounded-[2rem] border border-[var(--color-border)] bg-white/75 p-8 shadow-[var(--shadow-soft)] backdrop-blur">
        <p className="section-kicker">Terms</p>
        <h1 className="mt-4 font-display text-5xl leading-tight tracking-[-0.05em]">
          Terms of use
        </h1>
        <p className="mt-6 text-lg leading-8 text-[var(--color-muted)]">
          {legalCopy.terms}
        </p>
        <div className="mt-8 space-y-4 text-base leading-8 text-[var(--color-muted)]">
          <p>
            Replace this placeholder with production-approved commercial, usage, and
            liability language before public deployment.
          </p>
          <p>
            The current landing page form is presentational only. If you connect it to a
            live contact workflow, document the fulfillment and support expectations here.
          </p>
        </div>
        <Link
          href="/"
          className="mt-10 inline-flex text-sm font-semibold uppercase tracking-[0.18em] text-[var(--color-primary)] transition-colors hover:text-[var(--color-accent)]"
        >
          Return home
        </Link>
      </div>
    </main>
  );
}

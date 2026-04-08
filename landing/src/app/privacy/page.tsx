import Link from "next/link";

import { legalCopy } from "@/lib/site";

export default function PrivacyPage() {
  return (
    <main className="min-h-screen bg-[var(--color-bg)] px-5 py-14 text-[var(--color-text)] md:px-8 lg:px-10">
      <div className="mx-auto max-w-3xl rounded-[2rem] border border-[var(--color-border)] bg-white/75 p-8 shadow-[var(--shadow-soft)] backdrop-blur">
        <p className="section-kicker">Privacy</p>
        <h1 className="mt-4 font-display text-5xl leading-tight tracking-[-0.05em]">
          Privacy notice
        </h1>
        <p className="mt-6 text-lg leading-8 text-[var(--color-muted)]">
          {legalCopy.privacy}
        </p>
        <div className="mt-8 space-y-4 text-base leading-8 text-[var(--color-muted)]">
          <p>
            Replace this placeholder with production-approved privacy language before
            launch. The landing page should describe what user data is collected, how it
            is processed, and where contact requests are stored.
          </p>
          <p>
            If you wire the demo request form to a CRM, marketing automation system, or
            analytics stack, update this page to reflect that data flow accurately.
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

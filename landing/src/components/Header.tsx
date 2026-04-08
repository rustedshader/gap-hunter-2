import Link from "next/link";

import { navItems } from "@/lib/site";
import { Button } from "@/components/ui/button";

export function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-black/5 bg-[rgba(248,242,233,0.72)] backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-5 py-4 md:px-8 lg:px-10">
        <Link href="/" className="flex items-center gap-3 text-[var(--color-text)]">
          <span className="inline-flex size-10 items-center justify-center rounded-full border border-[var(--color-border-strong)] bg-[var(--color-primary)] text-sm font-bold tracking-[0.16em] text-[var(--color-cream)]">
            GH
          </span>
          <span className="flex flex-col">
            <span className="font-display text-lg leading-none tracking-[-0.03em]">
              Gap Hunter
            </span>
            <span className="text-xs uppercase tracking-[0.18em] text-[var(--color-muted)]">
              Policy Command Center
            </span>
          </span>
        </Link>
        <nav className="hidden items-center gap-7 text-sm font-medium text-[var(--color-muted)] md:flex">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="transition-colors hover:text-[var(--color-primary)]"
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-3">
          <Button asChild variant="ghost" className="hidden md:inline-flex">
            <Link href="#faq">See FAQ</Link>
          </Button>
          <Button asChild size="lg">
            <Link href="#book-demo">Book a walkthrough</Link>
          </Button>
        </div>
      </div>
    </header>
  );
}

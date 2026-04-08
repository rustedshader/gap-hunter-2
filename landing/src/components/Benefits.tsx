import { benefits, sectionEyebrows } from "@/lib/site";
import { Card, CardContent } from "@/components/ui/card";

export function Benefits() {
  return (
    <section
      id="benefits"
      className="px-5 py-18 md:px-8 md:py-24 lg:px-10"
      aria-labelledby="benefits-title"
    >
      <div className="mx-auto max-w-7xl">
        <div className="max-w-3xl">
          <p className="section-kicker">{sectionEyebrows.benefits}</p>
          <h2
            id="benefits-title"
            className="mt-4 font-display text-4xl leading-tight tracking-[-0.04em] text-[var(--color-text)] md:text-5xl"
          >
            The product earns trust by making policy work legible, reviewable, and faster to move.
          </h2>
          <p className="mt-5 text-lg leading-8 text-[var(--color-muted)]">
            Every section below maps to a real operational outcome, not a generic
            landing-page feature list.
          </p>
        </div>
        <div className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {benefits.map((benefit, index) => (
            <Card
              key={benefit.title}
              className={index === 0 ? "md:col-span-2 xl:col-span-2" : undefined}
            >
              <CardContent className="h-full">
                <div className="inline-flex rounded-[1.2rem] bg-[var(--color-accent)]/12 p-3 text-[var(--color-accent)]">
                  <benefit.icon className="size-5" />
                </div>
                <p className="mt-5 text-xs uppercase tracking-[0.2em] text-[var(--color-primary)]">
                  {benefit.highlight}
                </p>
                <h3 className="mt-3 font-display text-3xl leading-tight tracking-[-0.04em] text-[var(--color-text)]">
                  {benefit.title}
                </h3>
                <p className="mt-4 text-base leading-7 text-[var(--color-muted)]">
                  {benefit.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}

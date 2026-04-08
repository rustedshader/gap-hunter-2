import { sectionEyebrows, testimonials } from "@/lib/site";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card, CardContent } from "@/components/ui/card";

export function Testimonials() {
  return (
    <section
      id="proof"
      className="px-5 py-18 md:px-8 md:py-24 lg:px-10"
      aria-labelledby="testimonials-title"
    >
      <div className="mx-auto max-w-7xl">
        <div className="max-w-3xl">
          <p className="section-kicker">{sectionEyebrows.testimonials}</p>
          <h2
            id="testimonials-title"
            className="mt-4 font-display text-4xl leading-tight tracking-[-0.04em] text-[var(--color-text)] md:text-5xl"
          >
            Teams respond when the product feels like an operations instrument, not a one-shot AI stunt.
          </h2>
        </div>
        <div className="mt-10 grid gap-5 md:grid-cols-2">
          {testimonials.map((testimonial, index) => (
            <Card
              key={testimonial.quote}
              className={index === 0 ? "md:-translate-y-2" : index === 3 ? "md:translate-y-2" : undefined}
            >
              <CardContent>
                <div className="flex items-center gap-1 text-[var(--color-primary)]">
                  {[0, 1, 2, 3, 4].map((star) => (
                    <span
                      key={star}
                      aria-hidden="true"
                      className="text-lg leading-none"
                    >
                      *
                    </span>
                  ))}
                </div>
                <p className="mt-6 font-display text-3xl leading-tight tracking-[-0.04em] text-[var(--color-text)]">
                  “{testimonial.quote}”
                </p>
                <div className="mt-8 flex items-center gap-4">
                  <Avatar className="ring-2 ring-[var(--color-accent)]/25">
                    <AvatarFallback>{testimonial.initials}</AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="text-sm font-semibold uppercase tracking-[0.16em] text-[var(--color-primary)]">
                      Design partner
                    </p>
                    <p className="mt-1 text-sm leading-6 text-[var(--color-muted)]">
                      {testimonial.role}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}

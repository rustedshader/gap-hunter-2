"use client";

import { faqs, sectionEyebrows } from "@/lib/site";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger
} from "@/components/ui/accordion";

export function FAQ() {
  return (
    <section
      id="faq"
      className="px-5 py-18 md:px-8 md:py-24 lg:px-10"
      aria-labelledby="faq-title"
    >
      <div className="mx-auto grid max-w-7xl gap-10 lg:grid-cols-[0.85fr_1.15fr]">
        <div className="max-w-xl">
          <p className="section-kicker">{sectionEyebrows.faq}</p>
          <h2
            id="faq-title"
            className="mt-4 font-display text-4xl leading-tight tracking-[-0.04em] text-[var(--color-text)] md:text-5xl"
          >
            Questions policy owners ask before they trust a new review workflow.
          </h2>
          <p className="mt-5 text-lg leading-8 text-[var(--color-muted)]">
            The goal is not to overpromise. The goal is to show where Gap Hunter
            compresses effort and where human review still matters.
          </p>
        </div>
        <Accordion type="single" collapsible className="space-y-4">
          {faqs.map((item) => (
            <AccordionItem value={item.question} key={item.question}>
              <AccordionTrigger>{item.question}</AccordionTrigger>
              <AccordionContent>{item.answer}</AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </section>
  );
}

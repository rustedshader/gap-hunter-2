import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { MediaSection } from "@/components/MediaSection";
import { Benefits } from "@/components/Benefits";
import { Comparison } from "@/components/Comparison";
import { Architecture } from "@/components/Architecture";
import { TestingFramework } from "@/components/TestingFramework";
import { ResearchHighlights } from "@/components/ResearchHighlights";
import { PerformanceBenchmarks } from "@/components/PerformanceBenchmarks";
import { TechnicalDeepDive } from "@/components/TechnicalDeepDive";
import { LiveDemo } from "@/components/LiveDemo";
import { Testimonials } from "@/components/Testimonials";
import { FAQ } from "@/components/FAQ";
import { FinalCTA } from "@/components/FinalCTA";
import { softwareApplicationSchema } from "@/lib/site";

export default function Home() {
  const jsonLd = JSON.stringify(softwareApplicationSchema);

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: jsonLd }}
      />
      <div className="page-shell">
        <Header />
        <main>
          {/* Design direction:
             Editorial command center with warm parchment surfaces, deep green contrast,
             ember accents, and a serif-led hierarchy. The page favors asymmetry, strong
             typographic scale, and a product-first visual system over SaaS-template defaults. */}
          <Hero />
          <MediaSection />
          <Benefits />
          <Comparison />
          <Architecture />
          <TestingFramework />
          <PerformanceBenchmarks />
          <ResearchHighlights />
          <TechnicalDeepDive />
          <LiveDemo />
          <Testimonials />
          <FAQ />
          <FinalCTA />
        </main>
        <Footer />
      </div>
    </>
  );
}

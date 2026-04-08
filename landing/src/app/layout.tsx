import type { Metadata } from "next";
import { Fraunces, Manrope } from "next/font/google";

import { seoKeywords } from "@/lib/site";
import "./globals.css";

const fraunces = Fraunces({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["500", "600", "700"]
});

const manrope = Manrope({
  variable: "--font-body",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"]
});

export const metadata: Metadata = {
  metadataBase: new URL("https://gaphunter.app"),
  title: "Gap Hunter Studio | Policy Gap Analysis Command Center",
  description:
    "Turn policy PDFs into NIST-aligned gap analysis, revision-ready output, and roadmap artifacts through one desktop-first review workspace.",
  keywords: seoKeywords,
  openGraph: {
    title: "Gap Hunter Studio | Policy Gap Analysis Command Center",
    description:
      "Gap Hunter Studio turns source policy documents into gap analysis, revision output, and roadmap artifacts through one desktop-first workflow.",
    url: "https://gaphunter.app",
    siteName: "Gap Hunter Studio",
    images: [
      {
        url: "/images/og-gap-hunter.svg",
        width: 1200,
        height: 630,
        alt: "Gap Hunter Studio preview"
      }
    ],
    locale: "en_US",
    type: "website"
  },
  twitter: {
    card: "summary_large_image",
    title: "Gap Hunter Studio | Policy Gap Analysis Command Center",
    description:
      "Desktop-first policy gap analysis with live telemetry, revisions, and roadmap planning.",
    images: ["/images/og-gap-hunter.svg"]
  }
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${fraunces.variable} ${manrope.variable}`}>
        {children}
      </body>
    </html>
  );
}

import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: "https://gaphunter.app",
      lastModified: "2026-04-09",
      changeFrequency: "weekly",
      priority: 1
    },
    {
      url: "https://gaphunter.app/privacy",
      lastModified: "2026-04-09",
      changeFrequency: "monthly",
      priority: 0.3
    },
    {
      url: "https://gaphunter.app/terms",
      lastModified: "2026-04-09",
      changeFrequency: "monthly",
      priority: 0.3
    }
  ];
}

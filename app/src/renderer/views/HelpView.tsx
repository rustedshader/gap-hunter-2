import React, { useMemo, useState } from "react";
import { FAQ_SECTIONS, GLOSSARY } from "../data/help";

export default function HelpView() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");

  const questionMap = useMemo(() => {
    const map = new Map<string, string>();
    FAQ_SECTIONS.forEach((section) => {
      section.items.forEach((item) => map.set(item.id, item.question));
    });
    return map;
  }, []);

  const filteredSections = useMemo(() => {
    const needle = search.trim().toLowerCase();
    return FAQ_SECTIONS.map((section) => {
      if (category !== "all" && section.id !== category) {
        return { ...section, items: [] };
      }
      const items = section.items.filter((item) => {
        if (!needle) {
          return true;
        }
        const haystack = [
          item.question,
          item.answer,
          ...(item.bullets || []),
          ...(item.keywords || [])
        ]
          .filter(Boolean)
          .join(" ")
          .toLowerCase();
        return haystack.includes(needle);
      });
      return { ...section, items };
    }).filter((section) => section.items.length > 0);
  }, [category, search]);

  const totalResults = filteredSections.reduce(
    (total, section) => total + section.items.length,
    0
  );

  return (
    <div className="stack">
      <section className="card">
        <div className="card-header">
          <div>
            <h2>Help Center</h2>
            <span className="subtle">FAQ and onboarding answers</span>
          </div>
          <div className="meta-label">Results: {totalResults}</div>
        </div>
        <div className="help-controls">
          <input
            type="text"
            placeholder="Search questions"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <select value={category} onChange={(event) => setCategory(event.target.value)}>
            <option value="all">All categories</option>
            {FAQ_SECTIONS.map((section) => (
              <option key={section.id} value={section.id}>
                {section.title}
              </option>
            ))}
          </select>
        </div>
        <div className="help-hint">
          Browse by category or search for keywords like "revision", "run directory", or "demo".
        </div>
      </section>

      {filteredSections.length === 0 && (
        <section className="card">
          <div className="empty">No help articles match your search.</div>
        </section>
      )}

      {filteredSections.map((section) => (
        <section key={section.id} className="card">
          <div className="card-header">
            <div>
              <h2>{section.title}</h2>
              <span className="subtle">{section.description}</span>
            </div>
          </div>
          <div className="faq-grid">
            {section.items.map((item) => (
              <details key={item.id} id={`faq-${item.id}`} className="faq-item">
                <summary>{item.question}</summary>
                <div className="faq-answer">
                  {item.answer
                    .split("\n")
                    .filter(Boolean)
                    .map((line, index) => (
                      <p key={`${item.id}-p-${index}`}>{line}</p>
                    ))}
                  {item.bullets && item.bullets.length > 0 && (
                    <ul>
                      {item.bullets.map((bullet) => (
                        <li key={bullet}>{bullet}</li>
                      ))}
                    </ul>
                  )}
                  {item.related && item.related.length > 0 && (
                    <div className="faq-related">
                      <span>See also:</span>
                      <div className="faq-related-links">
                        {item.related.map((id) => (
                          <a key={id} href={`#faq-${id}`}>
                            {questionMap.get(id) || id}
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </details>
            ))}
          </div>
        </section>
      ))}

      <section className="card">
        <div className="card-header">
          <div>
            <h2>Glossary</h2>
            <span className="subtle">Common terms in Gap Hunter Studio</span>
          </div>
        </div>
        <div className="glossary-grid">
          {GLOSSARY.map((item) => (
            <div key={item.term} className="glossary-item">
              <strong>{item.term}</strong>
              <p>{item.definition}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

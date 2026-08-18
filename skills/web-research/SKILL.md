---
name: web-research
description: Research current or disputed topics on the web, fact-check claims, detect misleading framing, compare sources, and synthesize an evidence-backed answer with dates, citations, uncertainty, and source quality. Use for online lookup, news, product/legal/technical changes, misinformation analysis, literature review, and source verification.
---

# Research and fact-check carefully

Turn the request into atomic claims. For each claim, record the exact wording, date relevance, source, evidence, confidence, and what would falsify it.

## Source discipline

- prefer primary sources: official documents, laws, standards, datasets, research papers, filings, direct statements, and original measurements;
- use high-quality secondary sources for context, not as a substitute for primary evidence;
- compare independent sources and look for copied reporting, incentives, missing denominators, outdated versions, and conflicts of interest;
- verify publication date versus event date and use concrete dates for relative claims;
- distinguish fact, interpretation, prediction, opinion, satire, and allegation;
- quote only what is needed and preserve context.

## Misleading-claim checks

Check for cherry-picking, false causality, base-rate neglect, denominator changes, survivorship bias, misleading graphs, omitted uncertainty, equivocation, fake authority, impersonation, outdated screenshots, and claims that cannot be traced to a source. Do not label something false merely because it is surprising. Use **supported**, **partly supported**, **unsupported**, **misleading**, **false**, or **unverifiable**, with a concise reason and evidence.

## Output

Return:

1. bottom line;
2. claim-by-claim table;
3. source quality and dates;
4. conflicting evidence and uncertainty;
5. what the user should do or verify next.

Cite load-bearing claims. When no reliable source is found, say what was searched and why the evidence is insufficient.

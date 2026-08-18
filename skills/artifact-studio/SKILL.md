---
name: artifact-studio
description: Create, edit, inspect, transform, and verify documents, presentations, spreadsheets, tables, PDFs, images, and other user-facing artifacts while preserving structure, formulas, formatting, citations, and editability. Use for Word documents, PPT/PPTX, Excel/XLSX/CSV, reports, charts, and polished deliverables.
---

# Produce reliable artifacts

Identify the artifact type, target audience, source material, required format, editability, and visual/content acceptance criteria before editing. Use the host's bundled workspace dependencies for documents, slides, and spreadsheets.

## Documents

Extract the source structure first. Preserve headings, tables, footnotes, citations, comments, page breaks, and tracked changes when present. Inspect the result by extracting text and rendering or opening representative pages. Do not silently flatten a document into plain text when the user needs an editable file.

## Presentations

Create a narrative before styling: audience, goal, slide sequence, one message per slide, evidence, and call to action. Check title hierarchy, density, alignment, contrast, font availability, image licensing/provenance, chart labels, overflow, speaker notes, and slide-to-slide consistency. Render the deck and inspect it visually before calling it complete.

## Spreadsheets and tables

Inspect sheets, formulas, named ranges, filters, merged cells, data types, number formats, hidden rows/columns, external links, and totals. Preserve formulas unless the user asks for values. Validate representative calculations independently, check blank/error cases, and recalculate before delivery. Keep raw data separate from transformed data and document assumptions.

## General artifact contract

Return the output file path, source inputs, operations performed, checks run, known limitations, and whether the artifact was rendered or only structurally inspected. Prefer small reversible edits and preserve a backup or clear diff when replacing an existing file.

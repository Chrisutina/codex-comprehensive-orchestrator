---
name: simulation-biology
description: Design, implement, analyze, and verify computational simulations, scientific models, data analyses, and biology workflows with explicit assumptions, units, controls, provenance, reproducibility, and safety boundaries. Use for physics/engineering simulations, statistics, computational biology, genomics, bioinformatics, and scientific literature analysis.
---

# Do reproducible scientific work

Define the question, observable, model boundary, data provenance, and decision threshold before choosing an algorithm. Separate measured data, inferred values, simulated values, and speculative interpretation.

## Simulation workflow

- state equations, variables, units, initial/boundary conditions, parameter ranges, and numerical method;
- check dimensional consistency, conservation laws, stability, convergence, sensitivity, and limiting cases;
- compare against an analytic solution, benchmark, independent implementation, or observed data when possible;
- record random seeds, software versions, environment, inputs, outputs, and plots;
- expose assumptions and failure modes rather than presenting a plausible chart as proof.

## Biology and bioinformatics workflow

Clarify organism, assay/data type, reference build, identifiers, preprocessing, normalization, statistical design, multiple-testing policy, and biological interpretation. Preserve raw data, metadata, and provenance. Validate sample quality, batch effects, confounders, and reproducibility. Prefer established public databases and primary literature where appropriate.

Keep computational analysis, literature synthesis, and wet-lab action distinct. Follow applicable biosafety, ethics, privacy, and institutional rules. Do not provide harmful pathogen enhancement, evasion, or unsafe experimental procedures; redirect to safe, lawful, high-level or defensive assistance when needed.

## Deliverable

Return the model/data definition, method, assumptions, code or notebook paths, environment, validation evidence, results, uncertainty, and a reproducibility command or recipe.

---
layout: default
title: Docs README
diataxis: orientation
diataxis_type: orientation
audience: Documentation contributors
outcome: Understand the public documentation structure in this repository.
authority_boundary:
  - collection
workflow_boundary: read-only
evidence_shape:
  - architecture-boundary
public_status: rewritten
last_verified: 2026-05-07
---

# Docs README

The public site is built from this `docs/` directory with Jekyll.

Current documentation structure:

- `index.md`: public homepage
- `start.md`: reader routing
- `tutorials/`: learning paths
- `how-to/`: production task guides
- `reference/`: exact collection facts
- `explanation/`: architecture and boundary explanations
- `_data/`: controlled vocabularies and navigation
- `_templates/`: page templates for future docs
- `_includes/` and `_layouts/`: site shell

Every rewritten page should declare `diataxis_type`, `authority_boundary`,
`workflow_boundary`, `evidence_shape`, and `public_status`.

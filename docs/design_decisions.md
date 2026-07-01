# Design Decisions

## Why not parse Gherkin directly?

Parsing Gherkin is behave-model's responsibility. behave-format consumes the
canonical domain model, ensuring single source of truth and avoiding
duplicate parsing logic.

## Why mutate in place?

Consistent with behave-model's transformation patterns. The formatter
mutates the Project and returns it, making chaining natural.

## Why frozen Settings?

Prevents accidental mutation mid-pipeline. Settings are read at pipeline
start and never change during formatting.

## Why no auto-discovery of feature files?

The CLI accepts explicit paths. This is predictable and CI-friendly.

## Why only spaces for indentation?

Tabs are inconsistent across editors. Spaces guarantee identical output
everywhere. This matches Black's philosophy for Python.

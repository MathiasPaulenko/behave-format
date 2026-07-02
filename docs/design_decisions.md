# Design Decisions

This document explains the key design decisions behind behave-format and the
rationale for each.

## Why not parse Gherkin directly?

**Decision:** behave-format does not parse `.feature` files. It consumes a
`behave-model.Project` as input.

**Rationale:**

Parsing Gherkin is [behave-model](https://github.com/MathiasPaulenko/behave-model)'s
responsibility. By consuming the canonical domain model, behave-format:

- Avoids duplicate parsing logic
- Benefits from behave-model's validation
- Has a single source of truth for the Gherkin AST
- Can focus entirely on formatting concerns

If behave-format parsed Gherkin itself, any parsing bug would need to be fixed
in two places. The current architecture ensures consistency.

## Why mutate in place?

**Decision:** `format_project` and `format_feature` mutate the model in place
and return it.

**Rationale:**

Consistent with behave-model's transformation patterns. The formatter mutates
the `Project` and returns it, making chaining natural:

```python
project = load_project("features/")
formatted = format_project(project, Settings())
text = render_project(formatted, Settings())
```

Creating a deep copy for every formatting operation would be wasteful — the
input model is typically not needed after formatting.

## Why frozen Settings?

**Decision:** `Settings` is a frozen (immutable) dataclass.

**Rationale:**

Prevents accidental mutation mid-pipeline. Settings are read at pipeline start
and never change during formatting. If settings could be modified, a bug in one
stage could silently affect another stage's behavior.

```python
settings = Settings(indent=2)
settings.indent = 4  # raises AttributeError — caught at development time
```

For overrides, use `with_indent()` which returns a new `Settings` instance.

## Why no auto-discovery of feature files?

**Decision:** The CLI accepts explicit paths rather than searching for `.feature`
files automatically.

**Rationale:**

Explicit paths are:

- **Predictable** — you know exactly which files will be formatted
- **CI-friendly** — `behave-format --check features/` is unambiguous
- **Fast** — no filesystem scanning overhead
- **Safe** — no risk of accidentally formatting files outside your project

Auto-discovery can be achieved with shell globbing: `behave-format features/**/*.feature`.

## Why only spaces for indentation?

**Decision:** behave-format uses spaces exclusively, never tabs.

**Rationale:**

Tabs are inconsistent across editors — a tab might render as 2, 4, or 8 spaces
depending on configuration. Spaces guarantee identical output everywhere.

This matches [Black's philosophy](https://github.com/psf/black) for Python and
[gofmt](https://go.dev/blog/gofmt)'s approach for Go: one canonical style,
no ambiguity.

## Why sort tags alphabetically by default?

**Decision:** `sort_tags = true` by default.

**Rationale:**

Tag order carries no semantic meaning in Gherkin — `@smoke @auth` and `@auth @smoke`
are equivalent. Sorting alphabetically:

- Produces deterministic output (same tags → same order, always)
- Reduces diff noise (tags don't shuffle between developers)
- Makes tag lookup easier in large files

Users who need to preserve tag order can set `sort_tags = false`.

## Why not sort features and scenarios by default?

**Decision:** `sort_features = false` and `sort_scenarios = false` by default.

**Rationale:**

Unlike tags, feature and scenario order **can** matter:

- Test execution order may depend on file order
- Features may be organized by domain, not alphabetically
- Scenarios within a feature often follow a logical flow

Sorting is available as an opt-in for teams that want it.

## Why a 4-stage pipeline?

**Decision:** The pipeline is: normalize → sort → align → print.

**Rationale:**

Each stage has a clear, non-overlapping responsibility:

1. **Normalize** must run first — it produces a clean baseline
2. **Sort** must run after normalize — sorting dirty data is error-prone
3. **Align** must run after sort — alignment depends on final element order
4. **Print** must run last — it converts the final model to text

This ordering ensures idempotency: running the pipeline twice produces the same
output because each stage produces a canonical state.

## Why separate format and render functions?

**Decision:** The API has both `format_*` (mutate in place) and `render_*`
(format + return text) functions.

**Rationale:**

Different use cases:

- `format_project` — when you want to modify the model and continue working with it
- `render_project` — when you want formatted text without modifying the original model
- CLI uses `format_feature` + `print_feature` internally for efficiency

## Why no configuration file format other than pyproject.toml?

**Decision:** Configuration is only via `pyproject.toml` under `[tool.behave-format]`.

**Rationale:**

- `pyproject.toml` is the modern Python standard for project configuration
- Avoids inventing a new config format
- Keeps all project config in one place
- Consistent with tools like Ruff, Mypy, and pytest

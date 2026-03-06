# Release Notes — v3.5

## What's New

- Introduced `DebatePolicyEngine` OOP entrypoint and added public dataclasses `TaskMeta` and `HexagramState` in `debate_policy_engine.py`.
- Unified Phase 3 test-facing symbols: `from debate_policy_engine import DebatePolicyEngine, TaskMeta, HexagramState` now works directly.
- Renamed legacy `TaskMeta` TypedDict to `_TaskMetaV2` to avoid symbol collision while preserving internal compatibility.
- Added module-level documentation clarifying recommended interfaces and legacy compatibility structure.
- Added `docs/BREAKING_CHANGES.md` with migration guidance and compatibility notes.
- Verified exception-path behavior with `tests/test_phase3_exceptions.py` (4/4 passing).

## Breaking Change

- Public symbol semantics changed: `TaskMeta` now refers to a dataclass (previously TypedDict).
- Legacy structure remains available internally as `_TaskMetaV2`.

## Migration

- Prefer constructing `TaskMeta(...)` and `HexagramState(...)` via dataclass style.
- For legacy typed-dict flows, migrate to `_TaskMetaV2` internally or adapt callers to dataclass inputs.

## Validation

```bash
pytest -q tests/test_phase3_exceptions.py
# Result: 4 passed
```

# Changesets

Add a changeset to any PR that should be released. Create a markdown file in
this directory (any name, e.g. `fix-token-parsing.md`):

```md
---
"livekit-api": patch
---

Short description of the change, used in the release notes.
```

List one line per package the change should release:

- **Packages:** `livekit-rtc`, `livekit-api`, `livekit-protocol`
- **Types:**

  | Type | Example |
  |---|---|
  | `patch` | 1.5.1 → 1.5.2 |
  | `minor` | 1.5.1 → 1.6.0 |
  | `major` | 1.5.1 → 2.0.0 |
  | `patch-rc` | 1.5.1 → 1.5.2.rc1 |
  | `minor-rc` | 1.5.1 → 1.6.0.rc1 |
  | `major-rc` | 1.5.1 → 2.0.0.rc1 |
  | `next-rc` | 1.6.0.rc1 → 1.6.0.rc2 |
  | `promote` | 1.6.0.rc2 → 1.6.0 |

When several pending changesets touch the same package, the largest bump wins.
Mixing stable and rc types for one package, or combining `promote` with
anything else, is rejected. Only rc types are allowed on branches other than
`main`.

## How releases happen

1. Every PR is checked by the **Changeset** workflow; invalid changesets fail
   the check.
2. On each push to `main`, **Package Release** applies all pending changesets
   and opens (or updates) the `Release: ...` PR with the version bumps and
   release notes, then deletes the changesets it used.
3. Merging that release PR tags each bumped package, publishes it to PyPI and
   creates its GitHub Release.

Changes that don't need a release (docs, CI, tests) don't need a changeset.

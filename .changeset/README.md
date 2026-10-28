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
   release notes, then deletes the changesets it used. Changesets used by an
   rc release are kept instead (and recorded in `.changeset/pre.json`) until
   that package's next stable release, normally `promote`, whose release notes
   then list every change since the last stable version.
3. Merging that release PR tags each bumped package, publishes it to PyPI and
   creates its GitHub Release.

Changes that don't need a release (docs, CI, tests) don't need a changeset.

## Manual version bump

As a fallback, run the **Manual Version Bump** workflow with a package and
bump type. It opens a `release/<prefix>-v<version>` PR without reading any
changeset; merging it publishes the same way as a changeset release PR.
It doesn't touch `.changeset/`, so changesets kept from rc releases stay until
that package's next changeset stable release.

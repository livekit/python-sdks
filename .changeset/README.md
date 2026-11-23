# Changesets

Add a changeset to any PR that changes a published package. Create a markdown
file in this directory (any name, for example `fix-token-parsing.md`), or run
`verwalter changeset`:

```md
---
"livekit-api": patch
---

Short description of the change, for the user of the package.
```

- **Packages:** `livekit` (the code in `livekit-rtc/`), `livekit-api`, `livekit-protocol`. One line per package.
- **Levels:** `patch` for a fix, `minor` for an addition, `major` for a break.

Do not add the PR number: the release adds it. When several pending changesets
name the same package, the largest level wins. A change to `livekit-protocol`
also releases `livekit-api` as a patch, with no changeset for it.

A PR that needs no release (docs, CI, tests) gets the `internal` label.

Pre-releases (`1.6.0rc1`) are not a changeset level: run the Pre-release PR
workflow. For a major rc of `livekit-protocol`, also add a `patch` changeset for
`livekit-api`. See [RELEASING.md](../RELEASING.md).

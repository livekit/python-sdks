# Releasing python-sdks

This repository releases with [verwalter](https://github.com/livekit/verwalter).
The [verwalter cheat sheet](https://github.com/livekit/verwalter/blob/main/docs/cheat-sheet.md)
has the commands that every repository shares. This file holds what is
specific to this repository.

## Packages

| Package | Path | Tag | Goes to |
|---|---|---|---|
| `livekit` | `livekit-rtc` | `rtc-v<version>` | PyPI: 5 wheel platforms, sdist |
| `livekit-api` | `livekit-api` | `api-v<version>` | PyPI |
| `livekit-protocol` | `livekit-protocol` | `protocol-v<version>` | PyPI |

Each package keeps its version in `livekit/<module>/version.py`.

`livekit-api` depends on `livekit-protocol`. A release of `livekit-protocol`
also releases `livekit-api` as a patch. The release moves the
`livekit-protocol` requirement in `livekit-api/pyproject.toml` to the new
version, and to the next major for a major release.

## Workflows

| File | Trigger | Does |
|---|---|---|
| `changeset-check.yml` | A PR opens or changes | Fails a package change with no changeset. Builds and runs `twine check` on the release PR. |
| `release-pr.yml` | A push to `main` | Keeps the release PR `release/main` current. |
| `pre-release.yml` | Run by hand | Opens an rc PR from its branch. |
| `release-gate.yml` | A `release/*` PR or review | Requires the verwalter author and 2 approvals of the head commit. |
| `package-release.yml` | The release PR merges | Builds, tags, uploads to PyPI, publishes the docs. |
| `build-docs.yml` | Called by `package-release.yml` | Uploads the pdoc docs of a final version to S3. |

`changeset-check.yml` skips `renovate/*` branches. `release-gate.yml` is a
required check on `main`. The `gate` job of `package-release.yml` releases only
a merged PR from `verwalter-release[bot]`, or a run by hand from `main`. A run
by hand releases only a commit that is on `main`.

## Release

1. Merge the release PR. It needs 2 approvals of its head commit. A push to
   `main` regenerates the PR, and the approvals then count no more.
2. Watch the run of `package-release.yml`: `gh run list --workflow package-release.yml --limit 1`.

`verwalter publish` uploads with twine: the wheels first, the sdist last. A
version counts as on PyPI when its sdist is there, so a half upload stays a
draft, and a re-run uploads the missing files. The `verify` job checks the end
state. Each tag has a public GitHub release, and PyPI has each sdist. For a final version, the docs job of the package
must also be green.

## Pre-release

Run `gh workflow run pre-release.yml --ref <branch>`. The pending changesets
decide the packages and the levels. The rc is `1.6.0rc1` in `version.py` and on
PyPI, and `1.6.0-rc.1` in the tag. The changesets stay pending for the final
release.

<!-- TODO(livekit/verwalter#137): remove this paragraph once an rc includes the dependents it needs. -->
An rc includes only the packages with a pending changeset. For a major rc of
`livekit-protocol`, also add a `patch` changeset for `livekit-api`. Else the rc
PR leaves `livekit-api` at `livekit-protocol<3.0.0`, which excludes the rc, and
the API tests cannot install both packages.

The release gate covers only PRs into `main`. An rc PR into another branch
needs no approval, and its merge releases the rc.

## A release failed

Find the cause first. The
[recovery section](https://github.com/livekit/verwalter/blob/main/docs/release-workflows.md#recovery)
has the paths by cause.

| Situation | Command |
|---|---|
| A job failed for a transient reason | `gh run rerun <run-id> --failed` |
| The workflow needed a fix, now on `main` | `gh workflow run package-release.yml -f ref=<tag>` |
| `publish` failed a package with `HEAD changed the source since <tag>` | `gh workflow run package-release.yml -f ref=<tag> -f package=<package>` |
| A build failed. The builds run before the tag, so no tag exists. | Merge the fix to `main` without a changeset, then `gh workflow run package-release.yml` |
| The released commit is wrong | `verwalter release --abandon <tag>`, then a changeset and the next version |

The PyPI upload skips files that PyPI has, so a re-run is safe. PyPI never
replaces a version. Yank a broken version on PyPI and release the next one.

## Who to ask

The owners in `.github/CODEOWNERS`.

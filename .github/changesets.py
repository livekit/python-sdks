"""Consume pending .changeset/*.md files and bump package versions.

A changeset looks like:

    ---
    "livekit-rtc": patch
    "livekit-api": minor-rc
    ---

    Summary of the change.

Supported bump types: patch, minor, major, patch-rc, minor-rc, major-rc,
next-rc, promote. When several changesets touch the same package, the
largest bump wins (an explicit X-rc wins over next-rc). Mixing stable and
rc bumps, or combining promote with anything else, is an error.

Changesets used by an rc release are kept and recorded in .changeset/pre.json
(package -> file names) instead of being deleted, so later runs skip them. The
package's next stable release (normally promote) lists them in its release
notes and deletes them.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess

import click
from packaging.version import Version
from update_versions import PACKAGES, do_bump, do_prerelease, read_version

CHANGESET_DIR = pathlib.Path(".changeset")
# Changesets already released in an rc, kept until the package's stable release
PRE_STATE = CHANGESET_DIR / "pre.json"

# Names accepted in changeset frontmatter -> key in PACKAGES
PACKAGE_ALIASES = {
    "livekit": "livekit",
    "livekit-rtc": "livekit",
    "livekit-api": "livekit-api",
    "livekit-protocol": "livekit-protocol",
}

STABLE = {"patch": 1, "minor": 2, "major": 3}
RC = {"patch-rc": 1, "minor-rc": 2, "major-rc": 3}
BUMP_TYPES = set(STABLE) | set(RC) | {"next-rc", "promote"}


def parse_changeset(path: pathlib.Path) -> tuple[dict[str, str], str]:
    m = re.match(r"^---\s*\n(.*?)\n?---\s*\n?(.*)$", path.read_text(), re.DOTALL)
    if not m:
        raise click.ClickException(f"{path}: missing '---' frontmatter")

    bumps: dict[str, str] = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        lm = re.fullmatch(r'[\'"]?([\w.\-]+)[\'"]?\s*:\s*[\'"]?([\w\-]+)[\'"]?', line)
        if not lm:
            raise click.ClickException(f"{path}: cannot parse line {line!r}")
        name, kind = lm.groups()
        if name not in PACKAGE_ALIASES:
            raise click.ClickException(
                f"{path}: unknown package {name!r} (expected one of {sorted(PACKAGE_ALIASES)})"
            )
        if kind not in BUMP_TYPES:
            raise click.ClickException(
                f"{path}: unknown bump type {kind!r} (expected one of {sorted(BUMP_TYPES)})"
            )
        bumps[PACKAGE_ALIASES[name]] = kind
    return bumps, m.group(2).strip()


def resolve(package: str, kinds: set[str]) -> str:
    if "promote" in kinds:
        if len(kinds) > 1:
            raise click.ClickException(
                f"{package}: 'promote' cannot be combined with {sorted(kinds - {'promote'})}"
            )
        return "promote"

    stable = kinds & STABLE.keys()
    if stable and kinds - stable:
        raise click.ClickException(f"{package}: cannot mix stable and rc bumps ({sorted(kinds)})")
    if stable:
        return max(stable, key=STABLE.__getitem__)

    explicit_rc = kinds & RC.keys()
    if explicit_rc:
        return max(explicit_rc, key=RC.__getitem__)
    return "next-rc"


def validate(package: str, kind: str) -> None:
    cur = Version(read_version(pathlib.Path(PACKAGES[package])))
    if kind == "next-rc" and not (cur.pre and cur.pre[0] == "rc"):
        raise click.ClickException(f"{package}: next-rc requires an rc version (got {cur})")
    if kind == "promote" and not cur.is_prerelease:
        raise click.ClickException(f"{package}: promote requires a pre-release (got {cur})")


def apply(package: str, kind: str) -> None:
    if kind in STABLE:
        do_bump(package, kind)
    elif kind in RC:
        do_bump(package, kind.removesuffix("-rc"))
        do_prerelease(package, "rc")
    elif kind == "next-rc":
        do_prerelease(package, "rc")
    elif kind == "promote":
        do_bump(package, "release")


def changeset_origin(path: pathlib.Path, repo: str | None) -> str:
    """Return " (#123 by @user)" for the PR that added this changeset, or ""."""
    if not repo:
        return ""
    try:
        sha = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%H", "-1", "--", str(path)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        if not sha:
            return ""
        pr = subprocess.run(
            [
                "gh",
                "api",
                f"repos/{repo}/commits/{sha}/pulls",
                "--jq",
                '.[0] // empty | "\\(.number) \\(.user.login)"',
            ],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
    except (OSError, subprocess.CalledProcessError) as e:
        click.echo(f"warning: cannot resolve PR for {path}: {e}", err=True)
        return ""
    if len(pr) == 2:
        return f" (#{pr[0]} by @{pr[1]})"
    return f" ({sha[:7]})"


def kept_entries(names: list[str], package: str, repo: str | None) -> list[str]:
    """Release-note entries for this package from changesets kept since its rc releases."""
    entries = []
    for name in names:
        path = CHANGESET_DIR / name
        bumps, summary = parse_changeset(path)
        if summary and package in bumps:
            entries.append(f"`{bumps[package]}` {summary}{changeset_origin(path, repo)}")
    return entries


@click.command()
@click.option(
    "--rc-only",
    is_flag=True,
    default=False,
    help="Reject stable bumps (used for non-main branches).",
)
@click.option(
    "--notes",
    type=click.Path(dir_okay=False, path_type=pathlib.Path),
    default=None,
    help="Write release notes (markdown) to this file.",
)
@click.option(
    "--repo",
    envvar="GITHUB_REPOSITORY",
    default=None,
    help="owner/name used to look up the PR and author of each changeset (needs gh).",
)
@click.option(
    "--check",
    is_flag=True,
    default=False,
    help="Only validate the pending changesets; don't change any file.",
)
def main(rc_only: bool, notes: pathlib.Path | None, repo: str | None, check: bool) -> None:
    pre: dict[str, list[str]] = json.loads(PRE_STATE.read_text()) if PRE_STATE.exists() else {}
    kept = {name for names in pre.values() for name in names}
    # A kept changeset still owes its entry to the stable release notes.
    missing = sorted(name for name in kept if not (CHANGESET_DIR / name).exists())
    if missing:
        raise click.ClickException(
            f"changesets kept from rc releases are missing: {missing} "
            f"(restore them, or remove them from {PRE_STATE} on purpose)"
        )
    # Parse them now too, so a broken kept changeset fails the PR check
    # instead of the stable release.
    for name in sorted(kept):
        parse_changeset(CHANGESET_DIR / name)
    files = sorted(
        p
        for p in CHANGESET_DIR.glob("*.md")
        if p.name.lower() != "readme.md" and p.name not in kept
    )

    kinds: dict[str, set[str]] = {}
    summaries: dict[str, list[str]] = {}
    packages_of: dict[str, set[str]] = {}
    for path in files:
        bumps, summary = parse_changeset(path)
        packages_of[path.name] = set(bumps)
        if summary and not check:
            summary += changeset_origin(path, repo)
        for package, kind in bumps.items():
            kinds.setdefault(package, set()).add(kind)
            if summary:
                # Each entry shows the bump type its changeset asked for.
                summaries.setdefault(package, []).append(f"`{kind}` {summary}")

    resolved = {package: resolve(package, k) for package, k in kinds.items()}
    if rc_only:
        stable = {p: k for p, k in resolved.items() if k in STABLE or k == "promote"}
        if stable:
            raise click.ClickException(
                f"only rc releases are allowed from non-main branches (got {stable})"
            )
    # Validate everything before touching any version file.
    for package, kind in resolved.items():
        validate(package, kind)

    if check:
        click.echo(f"{len(files)} changeset(s) valid ({len(kept)} kept from rc releases).")
        for package in PACKAGES:
            if package in resolved:
                cur = read_version(pathlib.Path(PACKAGES[package]))
                click.echo(f"  {package}: {cur} ({resolved[package]})")
        return

    lines: list[str] = []
    released: list[str] = []
    for package in PACKAGES:  # stable order
        if package not in resolved:
            continue
        kind = resolved[package]
        apply(package, kind)
        version = read_version(pathlib.Path(PACKAGES[package]))
        released.append(f"{package} v{version}")
        lines.append(f"## {package} v{version} ({kind})\n")
        entries = summaries.get(package, [])
        if kind in RC or kind == "next-rc":
            # Keep this rc's changesets for the stable release notes.
            pre.setdefault(package, []).extend(
                p.name for p in files if package in packages_of[p.name]
            )
        else:
            # A stable release (normally promote) also lists the changesets
            # kept since this package's rc releases.
            entries = kept_entries(pre.pop(package, []), package, repo) + entries
        for summary in entries:
            lines.append("- " + summary.replace("\n", "\n  "))
        lines.append("")

    # Changesets are consumed once applied (including ones listing no package),
    # except those still kept for a package's stable release.
    still_kept = {name for names in pre.values() for name in names}
    for name in {p.name for p in files} | kept:
        if name not in still_kept:
            (CHANGESET_DIR / name).unlink(missing_ok=True)
    if pre:
        PRE_STATE.write_text(json.dumps(pre, indent=2, sort_keys=True) + "\n")
    else:
        PRE_STATE.unlink(missing_ok=True)

    if notes is not None:
        notes.write_text("\n".join(lines))

    title = ", ".join(released)
    print(f"Release: {title or '(nothing to release)'}")
    if gh_output := os.environ.get("GITHUB_OUTPUT"):
        with open(gh_output, "a") as f:
            f.write(f"title={title}\n")


if __name__ == "__main__":
    main()

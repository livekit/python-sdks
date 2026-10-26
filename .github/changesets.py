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
"""

from __future__ import annotations

import os
import pathlib
import re
import subprocess

import click
from packaging.version import Version
from update_versions import PACKAGES, do_bump, do_prerelease, read_version

CHANGESET_DIR = pathlib.Path(".changeset")

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


def check(package: str, kind: str) -> None:
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
def main(rc_only: bool, notes: pathlib.Path | None, repo: str | None) -> None:
    files = sorted(p for p in CHANGESET_DIR.glob("*.md") if p.name.lower() != "readme.md")

    kinds: dict[str, set[str]] = {}
    summaries: dict[str, list[str]] = {}
    for path in files:
        bumps, summary = parse_changeset(path)
        if summary:
            summary += changeset_origin(path, repo)
        for package, kind in bumps.items():
            kinds.setdefault(package, set()).add(kind)
            if summary:
                summaries.setdefault(package, []).append(summary)

    resolved = {package: resolve(package, k) for package, k in kinds.items()}
    if rc_only:
        stable = {p: k for p, k in resolved.items() if k in STABLE or k == "promote"}
        if stable:
            raise click.ClickException(
                f"only rc releases are allowed from non-main branches (got {stable})"
            )
    # Validate everything before touching any version file.
    for package, kind in resolved.items():
        check(package, kind)

    lines: list[str] = []
    released: list[str] = []
    for package in PACKAGES:  # stable order
        if package not in resolved:
            continue
        apply(package, resolved[package])
        version = read_version(pathlib.Path(PACKAGES[package]))
        released.append(f"{package} v{version}")
        lines.append(f"## {package} v{version} ({resolved[package]})\n")
        for summary in summaries.get(package, []):
            lines.append("- " + summary.replace("\n", "\n  "))
        lines.append("")

    # Changesets are consumed once applied (including ones listing no package).
    for path in files:
        path.unlink()

    if notes is not None:
        notes.write_text("\n".join(lines))

    title = ", ".join(released)
    print(f"Release: {title or '(nothing to release)'}")
    if gh_output := os.environ.get("GITHUB_OUTPUT"):
        with open(gh_output, "a") as f:
            f.write(f"title={title}\n")


if __name__ == "__main__":
    main()

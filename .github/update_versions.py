import pathlib
import re
import click
from packaging.version import Version

PACKAGES = {
    "livekit": "livekit-rtc/livekit/rtc/version.py",
    "livekit-api": "livekit-api/livekit/api/version.py",
    "livekit-protocol": "livekit-protocol/livekit/protocol/version.py",
}


def _esc(*codes: int) -> str:
    return "\033[" + ";".join(str(c) for c in codes) + "m"


def read_version(f: pathlib.Path) -> str:
    text = f.read_text()
    m = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', text)
    if not m:
        raise ValueError(f"could not find __version__ in {f}")
    return m.group(1)


def write_new_version(f: pathlib.Path, new_version: str) -> None:
    text = f.read_text()
    new_text = re.sub(
        r'__version__\s*=\s*[\'"][^\'"]*[\'"]',
        f'__version__ = "{new_version}"',
        text,
        count=1,
    )
    f.write_text(new_text)


def bump_version(cur: str, bump_type: str) -> str:
    v = Version(cur)
    if bump_type == "release":
        return v.base_version
    if bump_type == "patch":
        return f"{v.major}.{v.minor}.{v.micro + 1}"
    if bump_type == "minor":
        return f"{v.major}.{v.minor + 1}.0"
    if bump_type == "major":
        return f"{v.major + 1}.0.0"
    raise ValueError(f"unknown bump type: {bump_type}")


def bump_prerelease(cur: str, bump_type: str) -> str:
    v = Version(cur)
    base = v.base_version
    if bump_type == "rc":
        if v.pre and v.pre[0] == "rc":
            next_rc = v.pre[1] + 1
        else:
            next_rc = 1
        return f"{base}.rc{next_rc}"
    raise ValueError(f"unknown prerelease bump type: {bump_type}")


def update_api_protocol_dependency(new_protocol_version: str) -> None:
    """Update livekit-api's dependency on livekit-protocol."""
    pyproject = pathlib.Path("livekit-api/pyproject.toml")
    if not pyproject.exists():
        return
    old_text = pyproject.read_text()
    new_text = re.sub(
        r'"livekit-protocol>=[\w.\-]+,',
        f'"livekit-protocol>={new_protocol_version},',
        old_text,
    )
    if new_text != old_text:
        pyproject.write_text(new_text)
        print(f"Updated livekit-api dependency on livekit-protocol to >={new_protocol_version}")


def do_bump(package: str, bump_type: str) -> None:
    version_path = PACKAGES[package]
    vf = pathlib.Path(version_path)
    cur = read_version(vf)
    new = bump_version(cur, bump_type)
    print(f"{package}: {_esc(31)}{cur}{_esc(0)} -> {_esc(32)}{new}{_esc(0)}")
    write_new_version(vf, new)

    if package == "livekit-protocol":
        update_api_protocol_dependency(new)


def do_prerelease(package: str, prerelease_type: str) -> None:
    version_path = PACKAGES[package]
    vf = pathlib.Path(version_path)
    cur = read_version(vf)
    new = bump_prerelease(cur, prerelease_type)
    print(f"{package}: {_esc(31)}{cur}{_esc(0)} -> {_esc(32)}{new}{_esc(0)}")
    write_new_version(vf, new)

    if package == "livekit-protocol":
        update_api_protocol_dependency(new)


@click.command("bump")
@click.option(
    "--package",
    type=click.Choice(list(PACKAGES.keys())),
    required=True,
    help="Package to bump.",
)
@click.option(
    "--pre",
    type=click.Choice(["rc", "none"]),
    default="none",
    help="Pre-release type.",
)
@click.option(
    "--bump-type",
    type=click.Choice(["patch", "minor", "major", "release"]),
    default="patch",
    help="Type of version bump.",
)
def bump(package: str, pre: str, bump_type: str) -> None:
    if pre == "none":
        do_bump(package, bump_type)
    else:
        do_prerelease(package, pre)


if __name__ == "__main__":
    bump()

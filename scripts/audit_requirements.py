"""Select exported lockfile requirements for a Python version on this platform."""

import argparse
from pathlib import Path

from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
parser.add_argument("destination", type=Path)
parser.add_argument("--python-version", required=True)
args = parser.parse_args()

environment = default_environment()
environment["python_version"] = args.python_version
environment["python_full_version"] = args.python_version + ".99"
requirements = {}
for line in args.source.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    requirement = Requirement(line)
    if requirement.marker and not requirement.marker.evaluate(environment):
        continue
    specifiers = list(requirement.specifier)
    if requirement.url or len(specifiers) != 1 or specifiers[0].operator != "==":
        parser.error(f"Expected an exact registry version: {line}")
    name = canonicalize_name(requirement.name)
    version = specifiers[0].version
    if name in requirements and requirements[name] != version:
        parser.error(f"Conflicting versions for {name} on Python {args.python_version}")
    requirements[name] = version

if not requirements:
    parser.error("No requirements selected")
args.destination.write_text(
    "".join(f"{name}=={version}\n" for name, version in sorted(requirements.items()))
)

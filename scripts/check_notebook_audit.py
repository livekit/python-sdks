"""Fail notebook audits except for the explicitly tracked unpatched advisory."""

import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("report", type=Path)
args = parser.parse_args()
report = json.loads(args.report.read_text())
if "advisories" not in report or "metadata" not in report or "error" in report:
    parser.error("Expected a successful pnpm audit JSON response")

blocking = []
for advisory in report["advisories"].values():
    advisory_id = advisory.get("github_advisory_id")
    if advisory_id == "GHSA-vfj7-8cjw-p6xm" and advisory.get("patched_versions") == "<0.0.0":
        print(
            "::warning::braces GHSA-vfj7-8cjw-p6xm remains unpatched in notebook "
            "build tooling. The full finding is retained in the audit artifact."
        )
    else:
        blocking.append(advisory_id or advisory["id"])

if blocking:
    print(f"Blocking notebook advisories: {blocking}")
    raise SystemExit(1)

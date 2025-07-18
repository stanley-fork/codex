#!/usr/bin/env python3

import json
import subprocess
import sys
import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="""Stage a release for the npm module.

Run this after the GitHub Release has been created and use
`--release-version` to specify the version to release.
"""
    )
    parser.add_argument(
        "--release-version", required=True, help="Version to release, e.g., 0.3.0"
    )
    args = parser.parse_args()
    version = args.release_version

    gh_run = subprocess.run(
        [
            "gh",
            "run",
            "list",
            "--branch",
            f"rust-v{version}",
            "--json",
            "workflowName,url,headSha",
            "--jq",
            'first(.[] | select(.workflowName == "rust-release"))',
        ],
        stdout=subprocess.PIPE,
        check=True,
    )
    gh_run.check_returncode()
    workflow = json.loads(gh_run.stdout)
    sha = workflow["headSha"]

    print(f"should `git checkout {sha}`")

    current_dir = Path(__file__).parent.resolve()
    stage_release = subprocess.run(
        [
            current_dir / "stage_release.sh",
            "--version",
            version,
            "--workflow-url",
            workflow["url"],
            "--native",
        ]
    )
    stage_release.check_returncode()

    return 0


if __name__ == "__main__":
    sys.exit(main())

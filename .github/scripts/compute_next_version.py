#!/usr/bin/env python3
import argparse
import re
import subprocess

_VERSION_RE = re.compile(r"^v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")


def parse_release_version(version: str) -> tuple[int, int, int]:
    match = _VERSION_RE.match(version.strip())
    if not match:
        raise ValueError(
            f"Could not parse release version from {version!r}; expected format x.y.z",
        )

    return (
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch")),
    )


def get_latest_tag_version() -> str | None:
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0", "--match", "v*"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None

    tag = result.stdout.strip()
    if not tag:
        return None

    major, minor, patch = parse_release_version(tag)
    return f"{major}.{minor}.{patch}"


def compute_next_version(current: str, bump: str) -> str:
    major, minor, patch = parse_release_version(current)

    if bump == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1

    return f"{major}.{minor}.{patch}"


def compute_testpypi_version(run_number: int) -> str:
    base = get_latest_tag_version() or "0.0.0"
    return f"{base}.dev{run_number}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--testpypi-dev",
        action="store_true",
        help="Build a unique TestPyPI dev version from the latest release tag",
    )
    parser.add_argument("--run-number", type=int, help="CI run number for TestPyPI dev builds")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--current", help="Released version to bump from (x.y.z or vx.y.z)")
    source.add_argument(
        "--latest-tag",
        action="store_true",
        help="Use the latest v* git tag as the released version",
    )
    parser.add_argument("--bump", choices=["major", "minor", "patch"], default="patch")
    args = parser.parse_args()

    if args.testpypi_dev:
        if args.run_number is None:
            parser.error("--run-number is required with --testpypi-dev")
        print(compute_testpypi_version(args.run_number))
        return 0

    if not args.current and not args.latest_tag:
        parser.error("one of --current, --latest-tag, or --testpypi-dev is required")

    current = get_latest_tag_version() or "0.0.0" if args.latest_tag else args.current
    print(compute_next_version(current, args.bump))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

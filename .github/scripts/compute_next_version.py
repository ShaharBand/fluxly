#!/usr/bin/env python3
import argparse
import re


def compute_next_version(current: str, bump: str) -> str:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", current)
    if match:
        major, minor, patch = map(int, match.groups())
    else:
        # fallback: try X.Y
        match = re.match(r"^(\d+)\.(\d+)", current)
        if not match:
            raise SystemExit(f"Could not parse version from: {current!r}")
        major, minor = map(int, match.groups())
        patch = 0

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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", required=True)
    parser.add_argument("--bump", choices=["major", "minor", "patch"], default="patch")
    args = parser.parse_args()

    next_version = compute_next_version(args.current, args.bump)
    print(next_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


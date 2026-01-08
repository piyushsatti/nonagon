#!/usr/bin/env python3
"""
Developer bootstrap: install dev dependencies.

Usage:
python scripts/dev_setup.py
"""
from __future__ import annotations

import subprocess
import sys


def run(cmd: list[str]) -> int:
    print("$", " ".join(cmd))
    return subprocess.call(cmd)


def main() -> int:
    code = run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"]) or 0
    code = run([sys.executable, "-m", "pip", "install", "-e", ".[dev]"]) or code
    if code == 0:
        print("Development dependencies installed.")
    else:
        print("There was an issue installing development dependencies.")
    return code


if __name__ == "__main__":
    raise SystemExit(main())

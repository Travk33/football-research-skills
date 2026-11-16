#!/usr/bin/env python3
"""Run from any working directory using the repository's implementation."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from football_pipeline.cli import main

if __name__ == '__main__':
    raise SystemExit(main())

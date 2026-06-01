from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lcs.charts import DEFAULT_OUTPUT_DIR, DEFAULT_SUMMARY_INPUT, generate_charts


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate benchmark charts from summary.csv."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_SUMMARY_INPUT),
        help="Summary CSV file path.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where PNG charts will be written.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    output_paths = generate_charts(args.input, args.output)

    for output_path in output_paths.values():
        print(f"Chart exported to {output_path}")


if __name__ == "__main__":
    main()

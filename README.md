# Longest Common Subsequence - Algorithm Comparison

Practical comparison of Python implementations for solving the Longest Common Subsequence (LCS) problem.

This repository compares the same problem across three algorithmic strategies so their scaling behavior can be observed directly. It started as a college assignment and now serves as a compact technical study of algorithm behavior, benchmarking, and trade-offs.

## What is LCS?

Longest Common Subsequence is the problem of finding the longest subsequence shared by two sequences while preserving the relative order of elements.

## Subsequence vs Substring

A substring must be contiguous.

A subsequence preserves order but may skip characters.

Example using `ABCDE`:

- `BCD` is a substring
- `ACE` is a subsequence

## Implemented algorithms

- brute force
- recursive brute force
- dynamic programming

## Project goals

This repository compares the implemented strategies in terms of:

- execution time
- number of comparisons
- LCS length
- practical execution limits

## Why this project is interesting

The same problem is solved with very different approaches, which makes the repository useful for:

- analyzing time complexity in a concrete way
- discussing trade-offs between simplicity and scalability
- demonstrating why dynamic programming is powerful
- generating benchmark data for technical notes, classes, or presentations

## Project structure

```text
.
|-- pyproject.toml
|-- main.py
|-- scripts/
|-- src/lcs/
|-- data/
|   |-- database1/
|   `-- database2/
|-- results/
|   |-- legacy/
|   `-- current/
|       |-- benchmark.csv
|       |-- charts/
|       |-- summary.csv
|       `-- environment.md
`-- tests/
```

## How to run

Python 3.9+ is enough for the comparison and benchmark flow.

Chart generation uses an optional `matplotlib` dependency.

If you want to use the package module path, install the repository in editable mode:

```bash
python -m pip install -e .
```

If you also want chart generation support:

```bash
python -m pip install -e .[charts]
```

Run the automated test suite before publishing benchmark artifacts:

```bash
python -m unittest discover -s tests -v
```

The repository currently uses:

- `data/database1/` for larger input files
- `data/database2/` for smaller benchmark-friendly inputs

Run a single file comparison:

```bash
python main.py compare data/database2/Strings02.txt
```

Run the default example:

```bash
python main.py
```

Run a benchmark over a whole dataset:

```bash
python main.py benchmark data/database2
```

Export benchmark results to CSV:

```bash
python main.py benchmark data/database2 --output results/current/benchmark.csv
```

Each benchmark publication writes three artifacts to `results/current/`:

- `benchmark.csv`: raw rows for every warmup and measured run
- `summary.csv`: aggregated rows per input and algorithm
- `environment.md`: machine, command, and benchmark configuration metadata

Generate charts from the published summary:

```bash
python scripts/generate_charts.py --input results/current/summary.csv --output results/current/charts
```

This command writes:

- `results/current/charts/execution_time_by_input_size.png`
- `results/current/charts/comparisons_by_input_size.png`
- `results/current/charts/lcs_length_by_input_size.png`

The benchmark currently defaults to:

- 1 warmup run per input and algorithm
- 6 measured runs per input and algorithm
- 30 seconds timeout per benchmark subprocess

Run the package entry point after editable install:

```bash
python -m lcs.cli compare data/database2/Strings02.txt
```

## Example output

```text
File: data/database2/Strings02.txt
String A (2): BD
String B (2): BB

Algorithm             | Subsequence | Length | Comparisons | Time (ms) | Notes
----------------------+-------------+--------+-------------+-----------+------
Dynamic programming   | B           | 1      | 4           | 0.010000  | -
Brute force           | B           | 1      | 3           | 0.030000  | -
Recursive brute force | B           | 1      | 7           | 0.005000  | -
```

## Safety limits

Brute-force approaches grow exponentially and quickly become impractical. To keep the CLI usable, the project skips unsafe inputs by default:

- brute force: skips files with input length above 18
- recursive brute force: skips files with input length above 12

If you really want to run them anyway, use:

```bash
python main.py benchmark data/database2 --allow-slow
```


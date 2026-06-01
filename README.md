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
|-- src/lcs/
|-- data/
|   |-- database1/
|   `-- database2/
|-- results/
|   |-- legacy/
|   `-- current/
|-- tests/
`-- plans/
```

## How to run

Python 3.9+ is enough. There are no external dependencies.

If you want to use the package module path, install the repository in editable mode:

```bash
python -m pip install -e .
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
python main.py benchmark data/database2 --output-csv benchmark-results.csv
```

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

## Project status

This repository is an evolving technical study focused on correctness, benchmarking, and clear documentation of algorithm behavior.

## What can be explored next

This repository can be extended in a few practical directions without changing its core purpose:

- add automated benchmark report generation from CSV results
- compare runtime growth with the expected theoretical complexity of each algorithm
- add memoization as an intermediate strategy between pure recursion and dynamic programming
- improve benchmark visualization with charts or summary tables in the repository
- experiment with different input patterns, such as highly similar and highly distinct strings
- optimize the dynamic programming implementation for space usage on larger inputs

## Suggested talking points for a presentation

If you want to present this repository, a strong narrative is:

1. Introduce the LCS problem and explain why it is a classic algorithmic challenge.
2. Show that the repository implements the same problem with three different strategies.
3. Use a small input example to confirm that all approaches produce the same result.
4. Highlight how runtime and comparison counts change as the input size grows.
5. Point out where brute-force approaches stop being practical.
6. Explain why dynamic programming scales better for this problem.
7. Close by showing how the repository can be used as a benchmark and learning tool.

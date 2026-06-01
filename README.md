# Longest Common Subsequence

This project compares three strategies for solving the Longest Common Subsequence (LCS) problem:

- dynamic programming
- brute force
- recursive brute force

The repository started as a college assignment and now works as a small experiment platform for showing how algorithmic complexity changes runtime in practice.

## Why this project is interesting

The same problem is solved with very different approaches, which makes the repository useful for:

- analyzing time complexity in a concrete way
- discussing trade-offs between simplicity and scalability
- demonstrating why dynamic programming is powerful
- generating benchmark data for reports, classes, or presentations

## Project structure

```text
.
|-- Data.py
|-- dynamic.py
|-- bruteforce.py
|-- bfrecursive.py
|-- main.py
|-- DataBase1/
|-- DataBase2/
|-- Results-DataBase1/
`-- Results-DataBase2/
```

## How to run

Python 3.9+ is enough. There are no external dependencies.

Run a single file comparison:

```bash
python main.py compare DataBase2/Strings02.txt
```

Run the default example:

```bash
python main.py
```

Run a benchmark over a whole dataset:

```bash
python main.py benchmark DataBase2
```

Export benchmark results to CSV:

```bash
python main.py benchmark DataBase2 --output-csv benchmark-results.csv
```

## Safety limits

Brute-force approaches grow exponentially and quickly become impractical. To keep the CLI usable, the project skips unsafe inputs by default:

- brute force: skips files with input length above 18
- recursive brute force: skips files with input length above 12

If you really want to run them anyway, use:

```bash
python main.py benchmark DataBase2 --allow-slow
```

## Example output

```text
File: DataBase2/Strings02.txt
String A (2): BD
String B (2): BB

Algorithm             | Subsequence | Length | Comparisons | Time (ms) | Notes
----------------------+-------------+--------+-------------+-----------+------
Dynamic programming   | B           | 1      | 4           | 0.010000  | -
Brute force           | B           | 1      | 3           | 0.030000  | -
Recursive brute force | B           | 1      | 4           | 0.005000  | -
```

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

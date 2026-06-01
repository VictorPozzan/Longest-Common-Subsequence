from pathlib import Path


class Data:
    """Read input files containing two sequences, one per line."""

    def cleanData(self, path_file):
        return self.read_pair(path_file)

    def read_pair(self, path_file):
        path = Path(path_file)

        with path.open("r", encoding="utf-8") as file:
            lines = ["".join(line.split()) for line in file if line.strip()]

        if len(lines) < 2:
            raise ValueError(
                f"Expected at least two non-empty lines in '{path.as_posix()}'."
            )

        return lines[0], lines[1]

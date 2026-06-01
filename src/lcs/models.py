from dataclasses import dataclass


@dataclass
class RunResult:
    algorithm: str
    length: int
    elapsed_seconds: float
    comparisons: int
    subsequence: str
    status: str = "ok"
    message: str = ""

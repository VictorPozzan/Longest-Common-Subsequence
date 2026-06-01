from dataclasses import dataclass
from typing import Optional


@dataclass
class LCSResult:
    algorithm: str
    input_a: str
    input_b: str
    input_size_a: int
    input_size_b: int
    lcs: str
    lcs_length: int
    comparisons: int


@dataclass
class TimedRunResult:
    algorithm: str
    elapsed_seconds: float
    lcs_result: Optional[LCSResult] = None
    status: str = "completed"
    message: str = ""

    @property
    def comparisons(self):
        if self.lcs_result is None:
            return 0
        return self.lcs_result.comparisons

    @property
    def length(self):
        if self.lcs_result is None:
            return 0
        return self.lcs_result.lcs_length

    @property
    def subsequence(self):
        if self.lcs_result is None:
            return ""
        return self.lcs_result.lcs

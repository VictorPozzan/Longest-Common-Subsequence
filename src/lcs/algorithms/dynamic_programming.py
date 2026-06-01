from lcs.models import LCSResult


class DynamicLCS:
    algorithm_name = "dynamic_programming"

    def __init__(self):
        self.comp = 0

    def solve(self, string_a, string_b):
        self.comp = 0

        rows = len(string_a)
        cols = len(string_b)
        table = [[0] * (cols + 1) for _ in range(rows + 1)]

        for row in range(1, rows + 1):
            for col in range(1, cols + 1):
                self.comp += 1
                if string_a[row - 1] == string_b[col - 1]:
                    table[row][col] = table[row - 1][col - 1] + 1
                else:
                    table[row][col] = max(table[row - 1][col], table[row][col - 1])

        subsequence = self.find_subsequence(table, rows, cols, string_a, string_b)
        lcs_length = table[rows][cols]

        if lcs_length != len(subsequence):
            raise ValueError("Reconstructed LCS length does not match the DP table result.")

        return LCSResult(
            algorithm=self.algorithm_name,
            input_a=string_a,
            input_b=string_b,
            input_size_a=rows,
            input_size_b=cols,
            lcs=subsequence,
            lcs_length=lcs_length,
            comparisons=self.comp,
        )

    def lcs(self, string_a, string_b):
        return self.solve(string_a, string_b)

    def find_subsequence(self, table, row, col, string_a, string_b):
        lcs_chars = []

        while row > 0 and col > 0:
            if string_a[row - 1] == string_b[col - 1]:
                lcs_chars.append(string_a[row - 1])
                row -= 1
                col -= 1
            elif table[row - 1][col] >= table[row][col - 1]:
                row -= 1
            else:
                col -= 1

        lcs_chars.reverse()
        return "".join(lcs_chars)

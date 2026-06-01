from time import perf_counter


class DynamicLCS:
    def __init__(self):
        self.comp = 0

    def lcs(self, string_a, string_b):
        self.comp = 0
        start = perf_counter()

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

        sub_string = self.findSubString(table, rows, cols, string_a, string_b)
        execution_time = perf_counter() - start

        return table[rows][cols], execution_time, self.comp, sub_string

    def findSubString(self, table, row, col, string_a, string_b):
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

from time import perf_counter


class BFRecursiveLCS:
    def __init__(self):
        self.comp = 0

    def lcs(self, string_a, string_b):
        self.comp = 0
        start = perf_counter()
        subsequence = self.lcs_recursive(string_a, string_b)
        execution_time = perf_counter() - start

        return len(subsequence), execution_time, self.comp, subsequence

    def lcs_recursive(self, string_a, string_b):
        self.comp += 1

        if not string_a or not string_b:
            return ""

        if string_a[-1] == string_b[-1]:
            return self.lcs_recursive(string_a[:-1], string_b[:-1]) + string_a[-1]

        left = self.lcs_recursive(string_a[:-1], string_b)
        right = self.lcs_recursive(string_a, string_b[:-1])

        if len(left) >= len(right):
            return left

        return right

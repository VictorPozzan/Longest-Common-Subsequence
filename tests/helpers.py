from lcs.models import LCSResult


def assert_is_subsequence(test_case, candidate, sequence):
    index = 0

    for char in sequence:
        if index < len(candidate) and candidate[index] == char:
            index += 1

    test_case.assertEqual(index, len(candidate))


def assert_valid_result(test_case, result, string_a, string_b, expected_length):
    test_case.assertIsInstance(result, LCSResult)
    test_case.assertEqual(result.input_a, string_a)
    test_case.assertEqual(result.input_b, string_b)
    test_case.assertEqual(result.input_size_a, len(string_a))
    test_case.assertEqual(result.input_size_b, len(string_b))
    test_case.assertEqual(result.lcs_length, expected_length)
    test_case.assertEqual(result.lcs_length, len(result.lcs))
    test_case.assertGreaterEqual(result.comparisons, 0)
    assert_is_subsequence(test_case, result.lcs, string_a)
    assert_is_subsequence(test_case, result.lcs, string_b)

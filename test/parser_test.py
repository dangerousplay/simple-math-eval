import unittest
from ddt import ddt, data, unpack

from math_parser import MathParser, ParserException


@ddt
class ParserTestSpec(unittest.TestCase):

    @unpack
    @data(
        {'expression': '1 + 1', 'expected': 2},
        {'expression': '4 + 1 + 3 + 2', 'expected': 10},
        {'expression': '3 - 1', 'expected': 2},
        {'expression': '3 - 1 + 2', 'expected': 4},
        {'expression': '3 - 1 + (4)', 'expected': 6},
    )
    def test_sum_subtract(self, expression, expected):
        p = MathParser()
        result = p.parse(expression)

        self.assertEqual(result, expected)

    @unpack
    @data(
        {'expression': '1 + 1 / 2', 'expected': 1.5},
        {'expression': '4 + 1 * 2', 'expected': 6},
        {'expression': '4 / 2', 'expected': 2},
        {'expression': '2 * 4 / 2', 'expected': 4},
        {'expression': '(5 * 3) / 2', 'expected': 7.5},
        {'expression': '1 * 6 / (3)', 'expected': 2},
    )
    def test_div_mult(self, expression, expected):
        p = MathParser()
        result = p.parse(expression)

        self.assertEqual(result, expected)

    @unpack
    @data(
        {'expression': 'log2(1 + 1)', 'expected': 1},
        {'expression': 'sqrt(2 * 2)', 'expected': 2},
        {'expression': 'sqrt(4 * 4) + sqrt(4)', 'expected': 6},
        {'expression': 'sqrt(4 * 4) / sqrt(4)', 'expected': 2},
        {'expression': 'sqrt(sqrt(4 * 4))', 'expected': 2},
        {'expression': 'log2(sqrt(4 * 4))', 'expected': 2},
    )
    def test_function(self, expression, expected):
        p = MathParser()
        result = p.parse(expression)

        self.assertEqual(result, expected)

    @unpack
    @data(
        {'expression': '2 ^ 2', 'expected': 4},
        {'expression': '2 * 2 ^ 3', 'expected': 16},
        {'expression': '2 ^ 3 * 2', 'expected': 16},
        {'expression': '2 + (2 ^ 3)', 'expected': 10},
        {'expression': '2 ^ 0', 'expected': 1},
        {'expression': '0 ^ 2', 'expected': 0},
    )
    def test_exponential_function(self, expression, expected):
        p = MathParser()
        result = p.parse(expression)

        self.assertEqual(result, expected)        

    @unpack
    @data(
        {'expression': 'a = log2(1 + 1)', 'expected': {'a': 1}},
        {'expression': 'b = sqrt(2 * 2)', 'expected': {'b': 2}},
        {'expression': 'b = sqrt(4 * 4) \n a = sqrt(b)', 'expected': {'b': 4, 'a': 2}},
        {'expression': 'b = 4 / 2 \n a = b \n c = a / 2', 'expected': {'b': 2, 'a': 2, 'c': 1}},
    )
    def test_variable(self, expression, expected):
        p = MathParser()
        result = p.parse(expression)

        self.assertIsNone(result)

        self.assertEqual(p.variables, expected)

    @unpack
    @data(
        {'expression': '1 + 1 /'},
        {'expression': '1 +'},
        {'expression': '+'},
        {'expression': '-'},
        {'expression': '1 + ( 2'},
    )
    def test_unexpected_token(self, expression):
        p = MathParser()

        with self.assertRaises(ParserException):
            p.parse(expression)


if __name__ == '__main__':
    unittest.main()

"""Pruebas del motor de cálculo."""

import unittest

from engine import evaluate, format_number, to_fraction


def ev(expr, degrees=True, ans=0.0):
    ok, value = evaluate(expr, degrees, ans)
    return value if ok else False


class TestEvaluate(unittest.TestCase):
    def test_precedence(self):
        self.assertEqual(ev("2+3*4"), 14)

    def test_parentheses(self):
        self.assertEqual(ev("(2+3)*4"), 20)

    def test_power_right_associative(self):
        self.assertEqual(ev("2^3^2"), 512)

    def test_unary_minus(self):
        self.assertEqual(ev("-5+10"), 5)

    def test_factorial(self):
        self.assertEqual(ev("5!"), 120)
        self.assertEqual(ev("0!"), 1)

    def test_division_by_zero(self):
        ok, msg = evaluate("5/0", True, 0)
        self.assertFalse(ok)
        self.assertEqual(msg, "división por cero")

    def test_ln_domain(self):
        ok, _ = evaluate("ln(-1)", True, 0)
        self.assertFalse(ok)

    def test_sqrt_domain(self):
        ok, _ = evaluate("sqrt(-4)", True, 0)
        self.assertFalse(ok)

    def test_ans(self):
        self.assertEqual(ev("Ans+5", True, 10), 15)

    def test_degrees(self):
        self.assertAlmostEqual(ev("sin(90)", True), 1.0)

    def test_radians(self):
        self.assertAlmostEqual(ev("sin(pi/2)", False), 1.0)

    def test_tan_90_degrees_error(self):
        ok, _ = evaluate("tan(90)", True, 0)
        self.assertFalse(ok)

    def test_incomplete_operator(self):
        ok, msg = evaluate("2+", True, 0)
        self.assertFalse(ok)
        self.assertEqual(msg, "incompleta")

    def test_incomplete_paren(self):
        ok, _ = evaluate("(2+3", True, 0)
        self.assertFalse(ok)

    def test_percent_module(self):
        self.assertEqual(ev("7%3"), 1)

    def test_log_base_10(self):
        self.assertEqual(ev("log(100)"), 2)

    def test_decimals(self):
        self.assertAlmostEqual(ev("1.5*2"), 3.0)

    def test_empty(self):
        ok, _ = evaluate("", True, 0)
        self.assertFalse(ok)


class TestFormatNumber(unittest.TestCase):
    def test_integer(self):
        self.assertEqual(format_number(42.0), "42")

    def test_decimal_no_zeros(self):
        self.assertEqual(format_number(0.5), "0.5")

    def test_whole_float(self):
        self.assertEqual(format_number(3.0), "3")


class TestToFraction(unittest.TestCase):
    def test_half(self):
        self.assertEqual(to_fraction(0.5), "1/2")

    def test_third(self):
        self.assertEqual(to_fraction(1 / 3), "1/3")

    def test_eighth(self):
        self.assertEqual(to_fraction(0.125), "1/8")

    def test_irrational(self):
        self.assertIsNone(to_fraction(3.14159265358979))

    def test_integer(self):
        self.assertIsNone(to_fraction(5.0))


if __name__ == "__main__":
    unittest.main()

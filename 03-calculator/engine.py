"""Motor de cálculo de la calculadora científica.

Sin dependencias de GUI. Análisis léxico y sintáctico propio (no usa eval).
"""

import math
import re
from fractions import Fraction

MAX_VALUE = 1e308


class EngineError(Exception):
    """Error de sintaxis o de dominio en la expresión."""


# --- Léxico ---------------------------------------------------------------

TOKEN_RE = re.compile(
    r"""
    (?P<number>\d+(?:\.\d*)?|\.\d+)
  | (?P<name>[A-Za-zπ]+)
  | (?P<op>[-+*/^%!()])
    """,
    re.VERBOSE,
)

def _tan_degrees(x):
    """tan en grados; singularidades en 90+180k son error."""
    if (x - 90) % 180 == 0:
        raise ZeroDivisionError
    return math.tan(math.radians(x))


FUNCTIONS = {
    "sin": lambda x, deg: math.sin(math.radians(x)) if deg else math.sin(x),
    "cos": lambda x, deg: math.cos(math.radians(x)) if deg else math.cos(x),
    "tan": lambda x, deg: (
        _tan_degrees(x) if deg else math.tan(x)
    ),
    "log": lambda x, deg: math.log10(x),
    "ln": lambda x, deg: math.log(x),
    "sqrt": lambda x, deg: math.sqrt(x),
}

CONSTANTS = {"pi": math.pi, "e": math.e, "π": math.pi}


def tokenize(expr):
    tokens = []
    pos = 0
    while pos < len(expr):
        if expr[pos].isspace():
            pos += 1
            continue
        m = TOKEN_RE.match(expr, pos)
        if not m:
            raise EngineError("sintaxis")
        if m.lastgroup == "number":
            text = m.group()
            tokens.append(("number", float(text) if "." in text else float(text)))
        elif m.lastgroup == "name":
            tokens.append(("name", m.group()))
        else:
            tokens.append(("op", m.group()))
        pos = m.end()
    return tokens


# --- Parser descendente recursivo ----------------------------------------

PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2}


class Parser:
    def __init__(self, tokens, degrees, ans):
        self.tokens = tokens
        self.pos = 0
        self.degrees = degrees
        self.ans = ans

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def next(self):
        tok = self.peek()
        if tok is None:
            raise EngineError("incompleta")
        self.pos += 1
        return tok

    def parse(self):
        value = self.parse_additive()
        if self.pos != len(self.tokens):
            raise EngineError("sintaxis")
        return value

    def parse_additive(self):
        value = self.parse_multiplicative()
        while self.peek() and self.peek()[0] == "op" and self.peek()[1] in "+-":
            op = self.next()[1]
            right = self.parse_multiplicative()
            value = value + right if op == "+" else value - right
        return value

    def parse_multiplicative(self):
        value = self.parse_unary()
        while self.peek() and self.peek()[0] == "op" and self.peek()[1] in "*/%":
            op = self.next()[1]
            right = self.parse_unary()
            if op == "*":
                value *= right
            elif op == "/":
                if right == 0:
                    raise EngineError("división por cero")
                value /= right
            else:
                if right == 0:
                    raise EngineError("división por cero")
                value %= right
        return value

    def parse_unary(self):
        tok = self.peek()
        if tok and tok[0] == "op" and tok[1] in "+-":
            self.next()
            value = self.parse_unary()
            return -value if tok[1] == "-" else value
        return self.parse_power()

    def parse_power(self):
        base = self.parse_postfix()
        if self.peek() and self.peek() == ("op", "^"):
            self.next()
            # Asociativa a la derecha: 2^3^2 = 2^(3^2)
            exponent = self.parse_unary()
            try:
                result = base ** exponent
            except (OverflowError, ZeroDivisionError):
                raise EngineError("Error")
            if isinstance(result, complex):
                raise EngineError("Error")
            return result
        return base

    def parse_postfix(self):
        value = self.parse_primary()
        while self.peek() and self.peek() == ("op", "!"):
            self.next()
            if value < 0 or value != int(value):
                raise EngineError("factorial")
            if value > 170:
                raise EngineError("Error")
            value = math.factorial(int(value))
        return value

    def parse_primary(self):
        tok = self.next()
        if tok[0] == "number":
            return tok[1]
        if tok[0] == "op" and tok[1] == "(":
            value = self.parse_additive()
            closing = self.peek()
            if not closing:
                raise EngineError("incompleta")
            if closing != ("op", ")"):
                raise EngineError("sintaxis")
            self.next()
            return value
        if tok[0] == "op" and tok[1] == ")":
            raise EngineError("sintaxis")
        if tok[0] == "name":
            name = tok[1]
            if name == "Ans":
                return self.ans
            if name in CONSTANTS:
                return CONSTANTS[name]
            if name in FUNCTIONS:
                if self.peek() and self.peek() == ("op", "("):
                    self.next()
                    arg = self.parse_additive()
                    closing = self.peek()
                    if not closing:
                        raise EngineError("incompleta")
                    if closing != ("op", ")"):
                        raise EngineError("sintaxis")
                    self.next()
                else:
                    raise EngineError("sintaxis")
                try:
                    return FUNCTIONS[name](arg, self.degrees)
                except (ValueError, ZeroDivisionError, OverflowError):
                    raise EngineError("Error")
            raise EngineError("sintaxis")
        raise EngineError("sintaxis")


# --- API pública ----------------------------------------------------------


def evaluate(expr, degrees, ans):
    """Devuelve (True, resultado) o (False, motivo)."""
    expr = expr.strip()
    if not expr:
        return False, "vacía"
    # Incompleta: termina en operador, '(' o función sin argumento.
    if re.search(r"[-+*/^%(]\s*$", expr) or re.search(
        r"\b(sin|cos|tan|log|ln|sqrt|Ans|pi|e)\s*$", expr
    ):
        # 'e' al final puede ser constante completa; solo 'func(' y ops cuentan.
        if re.search(r"[-+*/^%(]\s*$", expr) or re.search(
            r"\b(sin|cos|tan|log|ln|sqrt)\s*$", expr
        ):
            return False, "incompleta"
    try:
        tokens = tokenize(expr)
    except EngineError:
        return False, "sintaxis"
    if not tokens:
        return False, "vacía"
    try:
        value = Parser(tokens, degrees, ans).parse()
    except EngineError as exc:
        if str(exc) == "incompleta":
            return False, "incompleta"
        return False, str(exc)
    except RecursionError:
        return False, "sintaxis"
    if isinstance(value, complex) or value != value or abs(value) == float("inf"):
        return False, "Error"
    if abs(value) > MAX_VALUE:
        return False, "Error"
    return True, value


def format_number(x):
    """Formato legible: sin notación salvo números muy grandes, sin ceros de más."""
    if x == int(x) and abs(x) < 1e16:
        return str(int(x))
    if abs(x) >= 1e16:
        return f"{x:.10g}"
    text = f"{x:.12f}".rstrip("0").rstrip(".")
    return text if text else "0"


def to_fraction(x):
    """Fracción equivalente exacta como texto, o None si no aplica."""
    try:
        frac = Fraction(x).limit_denominator(10000)
    except (ValueError, OverflowError):
        return None
    if frac.denominator == 1:
        return None
    if abs(float(frac) - x) > 1e-10:
        return None
    return f"{frac.numerator}/{frac.denominator}"

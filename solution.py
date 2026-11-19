import re

import pandas as pd

_LABEL_RE = re.compile(r"^[A-Za-z_]+$")
_COLUMN_RE = re.compile(r"[A-Za-z_]+")
_OPERATORS = "+-*"


def _tokenize(role: str):
    text = role.strip()
    if text == "":
        return None

    tokens = []
    position = 0
    length = len(text)
    expecting_operand = True

    while position < length:
        if text[position].isspace():
            position += 1
            continue

        if expecting_operand:
            match = _COLUMN_RE.match(text, position)
            if match is None:
                return None
            tokens.append(("col", match.group(0)))
            position = match.end()
            expecting_operand = False
        else:
            if text[position] not in _OPERATORS:
                return None
            tokens.append(("op", text[position]))
            position += 1
            expecting_operand = True

    if expecting_operand:
        return None
    return tokens


def _evaluate(tokens, df: pd.DataFrame):
    def column(name):
        if name not in df.columns:
            raise KeyError(name)
        return df[name]

    terms = []
    sign = 1
    current = column(tokens[0][1])

    position = 1
    while position < len(tokens):
        operator = tokens[position][1]
        operand = column(tokens[position + 1][1])
        if operator == "*":
            current = current * operand
        else:
            terms.append((sign, current))
            sign = 1 if operator == "+" else -1
            current = operand
        position += 2
    terms.append((sign, current))

    result = None
    for term_sign, series in terms:
        signed = series if term_sign == 1 else -series
        result = signed if result is None else result + signed
    return result


def add_virtual_column(df: pd.DataFrame, role: str, new_column: str) -> pd.DataFrame:
    if not _LABEL_RE.match(new_column):
        return pd.DataFrame([])

    tokens = _tokenize(role)
    if tokens is None:
        return pd.DataFrame([])

    try:
        values = _evaluate(tokens, df)
    except KeyError:
        return pd.DataFrame([])

    result = df.copy()
    result[new_column] = values
    return result

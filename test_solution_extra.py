import pandas as pd

from solution import add_virtual_column


def test_three_term_expression_respects_operator_precedence():
    df = pd.DataFrame({"a": [2, 10], "b": [3, 4], "c": [1, 5]})
    result = add_virtual_column(df, "a * b - c", "total")
    assert result["total"].tolist() == [5, 35]


def test_single_column_role_is_a_valid_expression():
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = add_virtual_column(df, "a", "copy_of_a")
    assert result["copy_of_a"].tolist() == [1, 2, 3]


def test_role_ending_in_operator_is_invalid():
    df = pd.DataFrame({"a": [1], "b": [2]})
    result = add_virtual_column(df, "a +", "c")
    assert result.empty


def test_new_column_with_digit_is_invalid_label():
    df = pd.DataFrame({"a": [1], "b": [2]})
    result = add_virtual_column(df, "a + b", "c1")
    assert result.empty


def test_empty_role_is_invalid():
    df = pd.DataFrame({"a": [1], "b": [2]})
    result = add_virtual_column(df, "", "c")
    assert result.empty


def test_does_not_mutate_the_input_dataframe():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    add_virtual_column(df, "a + b", "c")
    assert list(df.columns) == ["a", "b"]


def test_works_on_an_empty_dataframe_with_matching_columns():
    df = pd.DataFrame({"a": [], "b": []})
    result = add_virtual_column(df, "a + b", "c")
    assert list(result.columns) == ["a", "b", "c"]
    assert len(result) == 0

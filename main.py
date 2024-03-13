import csv
from functools import wraps
from time import perf_counter_ns

import pandas as pd
import polars as pl
from rich import pretty, print, table

pretty.install()
table = table.Table()
table.add_column("Function", justify="center")
table.add_column("Time in ns", justify="center")
table.add_column("VS. Python", justify="center")

benchmarks = {}
file = "./data.csv"


def benchmark(f):
    @wraps(f)
    def new_f(*args, **kwargs):
        start = perf_counter_ns()
        result = f(*args, **kwargs)
        end = perf_counter_ns() - start

        scores = benchmarks.get(f.__name__)

        if scores:
            benchmarks[f.__name__] = [*scores, end]
        else:
            benchmarks[f.__name__] = [end]

        return result

    return new_f


@benchmark
def read_csv_in_python(path):
    with open(path, 'r+') as f:
        obj = csv.reader(f, delimiter=',')
        return list(obj)


@benchmark
def read_csv_in_pandas(path):
    return pd.read_csv(path)


@benchmark
def read_csv_in_polars(path):
    return pl.read_csv(path)


def get_scores():
    result = {}

    for func_name, scores in benchmarks.items():
        result[func_name] = sum(scores) / len(scores)

    return result


def compare_with_python(python_score, score):
    if python_score == score:
        return "-"

    if python_score < score:
        return f"-{python_score / score * 100}%"

    return f"+{(score / python_score) * 100}%"


def show_results():
    scores = get_scores()

    python_score = scores[read_csv_in_python.__name__]

    for func_name, score in scores.items():
        table.add_row(func_name, str(score), str(compare_with_python(python_score, score)))

    print(table)


for i in range(100):
    read_csv_in_python(file)
    read_csv_in_pandas(file)
    read_csv_in_polars(file)

show_results()

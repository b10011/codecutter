# CodeCutter

CodeCutter is a Python library designed to preprocess Python functions and methods by performing compile-time optimizations. Inspired by the behavior of the C preprocessor, CodeCutter enhances execution performance by simplifying code logic before it runs, focusing on optimizing variables and control flow statements.

## Features

- Replace variables with constants or expressions: Automatically replaces variables with constant values or constant expressions when detected. This allows for faster execution as it reduces the need for variable lookups during runtime.
- Simplify boolean if-clauses with constants: If a boolean expression contains constants, CodeCutter simplifies the expression by evaluating it during preprocessing. This can eliminate unnecessary branches in your code.
- Remove dead if-clauses: If certain conditions in if statements are known to always evaluate to True or False, CodeCutter removes or short-circuits these branches. This only includes unreachable code due to constants, not always-true conditions.

## Why CodeCutter?

Unlike regex-based or hacky import-time solutions, CodeCutter operates in a clean and structured way, leveraging Python’s internal structures to perform safe and reliable transformations. The library is built with extensibility in mind, allowing you to easily add custom preprocessing logic to match your specific optimization needs.

## Documentation

[A small documentation](https://github.com/b10011/codecutter/blob/master/documentation.md)

## Installation

You can install CodeCutter using pip:

```bash
pip3 install codecutter
```

## Examples

Here's an example of how CodeCutter can improve your function before runtime.

Original bad function

```python3
def bad_function(
    iterations,
    feature_a_enabled,
    feature_b_enabled,
    feature_c_enabled,
):
    my_sum = 0

    for i in range(iterations):
        if feature_a_enabled:
            my_sum += 1

        if feature_b_enabled:
            my_sum += 2

        if feature_c_enabled:
            my_sum += 3

        my_sum += i

bad_function(10000, False, False, False)
```

The same function with preprocessing. Do note that the values of the constants
are given as strings. This is so that the system can replace constants even with
e.g. comparisons such as `"value >= 5"` or function calls. If you utilize
variables outside of the function body (e.g. decorators), pass those to the
preprocessor with `variables` kwarg.

```python3
from codecutter import preprocess

@preprocess(
    constants={
        "FEATURE_A_ENABLED": "False",
        "FEATURE_B_ENABLED": "False",
        "FEATURE_C_ENABLED": "False",
    }
)
def good_function(iterations):
    my_sum = 0

    for i in range(iterations):
        if FEATURE_A_ENABLED:
            my_sum += 1

        if FEATURE_B_ENABLED:
            my_sum += 2

        if FEATURE_C_ENABLED:
            my_sum += 3

        my_sum += i

good_function(10000)
```

The source code of the preprocessed function

```python3
def good_function(iterations):
    my_sum = 0
    for i in range(iterations):
        my_sum += i
```

Performance difference (best of 5 runs with `%timeit`)

- Original: `267 µs ± 7.32 µs per loop (mean ± std. dev. of 7 runs, 1,000 loops each)`
- Preprocessed: `196 µs ± 5.57 µs per loop (mean ± std. dev. of 7 runs, 1,000 loops each)`

Over 26% improvement!

## Contributing & TODO

Preprocess expressions such as `1 + 2 + 3 * value * 4` -> `3 + 12 * value`

Preprocess sequential binary opterations such as `i += 1` + `i += 2` -> `i += 3`

Detect deep attribute fetching in loops and replace (applies to non-functions too)

```python3
for i in range(1000):
    self.operations["myfunction"](i)
```

with

```python3
f = self.operations["myfunction"]
for i in range(1000):
    f(i)
```

## Footnote

ChatGPT seems to excel at README's.

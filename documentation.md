# Documentation

## Constants and remove dead code branches

```python3
from codecutter import preprocess

@preprocess(constants={"MULTIPLIER": "5", "CONDITION": "True"})
def function(value):
    if CONDITION:
        return value * MULTIPLIER
    else:
        return value - 1
```

Above is preprocessed to

```python3
def function(value):
    return value * 5
```

## Replace with expression

```python3
from codecutter import preprocess

@preprocess(constants={"MULTIPLIER": "5", "CONDITION": "value <= 4"})
def function(value):
    if CONDITION:
        return value * MULTIPLIER
    else:
        return value - 1
```

Above is preprocessed to

```python3
def function(value):
    if value <= 4:
        return value * 5
    else:
        return value - 1
```

## Other decorators

Do note that the other decorators must be applied above the preprocess
decorator! Otherwise the preprocessing is done to the next decorator.

```python3
from codecutter import preprocess

def halve(f):
    def wrapper(v):
        return f(v) / 2
    return wrapper

@halve
@preprocess(constants={"MULTIPLIER": "5", "CONDITION": "True"})
# <--- Do not add decorators between @preprocess and the function  --->
def function(value):
    if CONDITION:
        return value * MULTIPLIER
    else:
        return value - 1
```

Above is preprocessed to

```python3
@halve
def function(value):
    return value * 5
```

## Custom preprocessing

```python3
from codecutter import preprocess
from codecutter.astwalk import walk
import ast

def uppercase_variables(function_tree):
    changed = False
    for container, index, item in list(walk(function_tree)):
        if isinstance(item, ast.Name):
            if item.id != item.id.upper():
                print("CHANGING", item.id, item.id.upper())
                item.id = item.id.upper()
                changed = True

    return changed


@preprocess(
    additional_preprocessors=[uppercase_variables],
)
def function(value):
    if value <= 5:
        return value * 2
    else:
        return value / 2
```

Above is preprocessed to

```python3
def function(value):
    if VALUE <= 5:
        return VALUE * 2
    else:
        return VALUE / 2
```

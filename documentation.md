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

## Methods

```python3
from codecutter import preprocess

class MyTest:
    def __init__(self, added_value):
        self.added_value = added_value

    @preprocess(constants={"MULTIPLIER": "5", "CONDITION": "True"})
    def function(value):
        if CONDITION:
            return value * MULTIPLIER + self.added_value
        else:
            return value - 1 + self.added_value
```

Above is preprocessed to

```python3
class MyTest:
    def __init__(self, added_value):
        self.added_value = added_value

    def function(value):
        return value * 5 + self.added_value
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

## Re-preprocessing [experimental, subject to changes]

As the bytecode is not replaced in-place, the reference to the preprocessed
function differs from the original. Therefore the "in-place" repreprocessing
utilizes a container for the function, in which the function can be replaced.
It has minimal effect on regular use, but keep in mind that after decorating,
the attribute you think is a function, is actually an instance of
`repreprocessable`. And if you are calling the function at high frequency, you
might want to manually call preprocess and replace an attribute in your class
to reduce the overhead created by the separate `repreprocessable` class.

Example with a function

```python3
from codecutter import repreprocessable

@repreprocessable
def myfunction(value):
    if CONDITION:
        return value * MULTIPLIER * 2
    else:
        return value * MULTIPLIER * 3

myfunction.preprocess(constants={"CONDITION": "True", "MULTIPLIER": "5"})

if myfunction(10) == 100:
    print("OK")

myfunction.preprocess(constants={"CONDITION": "False", "MULTIPLIER": "5"})

if myfunction(10) == 150:
    print("OK")

myfunction.preprocess(constants={"CONDITION": "True", "MULTIPLIER": "8"})

if myfunction(10) == 160:
    print("OK")
```

Example with a method. Note how the instance of the class must be passed as the
first argument so that the preprocessed method can be bound to the original
instance. As this is quite inconvenient, it is likely to change in the future.
This is intented to be used in cases when there is "configuration" that changes,
but does so rarely. Each time the configuration changes, run the preprocessing
with new values and the code is optimized again.

```python3
class MyTest:
    def __init__(self, added_value):
        self.added_value = added_value

    @repreprocessable
    def myfunction(self, value):
        if CONDITION:
            return value * MULTIPLIER * 2 + self.added_value
        else:
            return value * MULTIPLIER * 3 + self.added_value

test = MyTest(123)

test.myfunction.preprocess(test, constants={"CONDITION": "True", "MULTIPLIER": "5"})

if test.myfunction(10) == 100 + 123:
    print("OK")

test.myfunction.preprocess(test, constants={"CONDITION": "False", "MULTIPLIER": "5"})

if test.myfunction(10) == 150 + 123:
    print("OK")

test.myfunction.preprocess(test, constants={"CONDITION": "True", "MULTIPLIER": "8"})

if test.myfunction(10) == 160 + 123:
    print("OK")
```

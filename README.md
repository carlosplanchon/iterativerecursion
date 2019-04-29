# iterativerecursion
*Python3 module to simulate recursion with iteration.*

This is a module I've done because I need something like this and
in part as a little experiment.

## Installation
### Install with pip
```
pip3 install -U iterativerecursion
```

## Usage
```
from iterativerecursion import IterativeRecursionEngine


def func_1_to_test(a: int) -> FunctionReturn:
    """
    Print a number.
    :param a: int: Number to print.

    """
    print(f"a: {a}")
    return dict(
        call_arg_n_func=dict(b="global_a"),
        next_function_to_call="func_2_to_test",
        returned_values=dict(global_a=a + 1)
        )


def func_2_to_test(b: int) -> FunctionReturn:
    """
    Print a number.
    :param b: int: Number to print.

    """
    print("b", b)
    return dict(
        call_arg_n_func=dict(),
        next_function_to_call=None,
        returned_values=dict()
        )


executor = IterativeRecursionEngine()
executor.add_function(func_1_to_test)
executor.add_function(func_2_to_test)
executor.start_function_caller(
    next_function_to_call="func_1_to_test",
    enviroment_variables=dict(test_var=2),
    call_arg_n_func=dict(a="test_var")
    )

```
Output:
```
a: 2
b 3
```

Be careful with infinite loops:
```
from iterativerecursion import IterativeRecursionEngine


def func_1_to_test(a: int) -> FunctionReturn:
    """
    Print a number.
    :param a: int: Number to print.

    """
    print(f"a: {a}")
    return dict(
        call_arg_n_func=dict(a="global_a"),
        next_function_to_call="func_1_to_test",
        returned_values=dict(global_a=a + 1)
        )


executor = IterativeRecursionEngine()
executor.add_function(func_1_to_test)
executor.start_function_caller(
    next_function_to_call="func_1_to_test",
    enviroment_variables=dict(test_var=0),
    call_arg_n_func=dict(a="test_var")
    )
```

Output:
```
a: 0
a: 1
a: 2
...
```

Import types used on this module:
```
from iterativerecursion import FunctionReturn, VarsDict
```

# iterativerecursion

*A Python module to simulate recursive function calls using iteration, providing explicit control over execution flow and avoiding stack overflow issues.*

## Overview

`iterativerecursion` provides a mechanism to chain function calls iteratively while maintaining a recursive-like pattern. Instead of relying on the call stack, functions explicitly declare what to call next, making the execution flow transparent and controllable.

### Why Use This?

- **Avoid Stack Overflow**: Handle deep recursion without hitting Python's recursion limit
- **Explicit Control**: See and control the exact flow of function calls
- **Debugging**: Easier to trace execution without deep call stacks
- **State Management**: Shared environment for passing data between functions
- **Safety**: Built-in iteration limits to prevent infinite loops

### When to Use This

This library is useful when you need:
- Deep recursion that exceeds Python's stack limit (~1000 calls)
- Explicit control over recursive execution flow
- To convert recursive algorithms to iterative ones systematically
- State machines or complex control flow patterns

For most cases, **normal recursion is simpler and preferred**. Use this when recursion depth or explicit control becomes a concern.

## Installation

### Using uv
```bash
uv add iterativerecursion
```

### Using pip
```bash
pip install iterativerecursion
```

## Quick Start

```python
from iterativerecursion import IterativeRecursionEngine, FunctionReturn

def greet(name: str) -> FunctionReturn:
    print(f"Hello, {name}!")
    return {
        "arg_env_mapping": {"name": "next_name"},
        "next_function_to_call": "farewell",
        "returned_values": {"next_name": "World"}
    }

def farewell(name: str) -> FunctionReturn:
    print(f"Goodbye, {name}!")
    return {
        "arg_env_mapping": {},
        "next_function_to_call": None,  # None terminates execution
        "returned_values": {}
    }

# Create engine and register functions
engine = IterativeRecursionEngine()
engine.add_function(greet)
engine.add_function(farewell)

# Start execution
engine.start_function_caller(
    next_function_to_call="greet",
    environment_variables={"initial_name": "Alice"},
    arg_env_mapping={"name": "initial_name"}
)
```

**Output:**
```
Hello, Alice!
Goodbye, World!
```

## How It Works

Functions return a structured dictionary (`FunctionReturn`) with three keys:

| Key | Type | Description |
|-----|------|-------------|
| `next_function_to_call` | `str \| None` | Name of the next function to execute, or `None` to stop |
| `returned_values` | `dict[str, Any]` | Values to store in the shared environment |
| `arg_env_mapping` | `dict[str, str]` | Mapping of parameter names to environment variable keys |

The engine maintains a shared environment where functions can store and retrieve values across calls.

## Examples

### Using the @register Decorator

The `@register` decorator provides a cleaner way to register functions:

```python
from iterativerecursion import IterativeRecursionEngine, FunctionReturn

engine = IterativeRecursionEngine()

@engine.register
def greet(name: str) -> FunctionReturn:
    print(f"Hello, {name}!")
    return {
        "arg_env_mapping": {"name": "next_name"},
        "next_function_to_call": "farewell",
        "returned_values": {"next_name": "World"}
    }

@engine.register
def farewell(name: str) -> FunctionReturn:
    print(f"Goodbye, {name}!")
    return {
        "arg_env_mapping": {},
        "next_function_to_call": None,
        "returned_values": {}
    }

# Start execution and get final state
result = engine.start_function_caller(
    next_function_to_call="greet",
    environment_variables={"initial_name": "Alice"},
    arg_env_mapping={"name": "initial_name"}
)
```

### Factorial Calculation

```python
from iterativerecursion import IterativeRecursionEngine, FunctionReturn

def factorial_step(n: int, accumulator: int) -> FunctionReturn:
    if n <= 1:
        return {
            "arg_env_mapping": {},
            "next_function_to_call": None,
            "returned_values": {"result": accumulator}
        }
    return {
        "arg_env_mapping": {"n": "n", "accumulator": "accumulator"},
        "next_function_to_call": "factorial_step",
        "returned_values": {
            "n": n - 1,
            "accumulator": accumulator * n
        }
    }

engine = IterativeRecursionEngine()
engine.add_function(factorial_step)
engine.start_function_caller(
    next_function_to_call="factorial_step",
    environment_variables={"n": 5, "accumulator": 1},
    arg_env_mapping={"n": "n", "accumulator": "accumulator"}
)

print(f"5! = {engine.environment_variables['result']}")  # Output: 5! = 120
```

### Fibonacci Sequence

```python
from iterativerecursion import IterativeRecursionEngine, FunctionReturn

def fibonacci(n: int, a: int, b: int) -> FunctionReturn:
    if n == 0:
        return {
            "arg_env_mapping": {},
            "next_function_to_call": None,
            "returned_values": {"result": a}
        }
    return {
        "arg_env_mapping": {"n": "n", "a": "a", "b": "b"},
        "next_function_to_call": "fibonacci",
        "returned_values": {
            "n": n - 1,
            "a": b,
            "b": a + b
        }
    }

engine = IterativeRecursionEngine()
engine.add_function(fibonacci)
engine.start_function_caller(
    next_function_to_call="fibonacci",
    environment_variables={"n": 10, "a": 0, "b": 1},
    arg_env_mapping={"n": "n", "a": "a", "b": "b"}
)

print(f"Fibonacci(10) = {engine.environment_variables['result']}")  # Output: 55
```

### Preventing Infinite Loops

Use the `max_iterations` parameter to prevent runaway execution:

```python
from iterativerecursion import IterativeRecursionEngine, FunctionReturn

def infinite_loop(counter: int) -> FunctionReturn:
    print(f"Iteration: {counter}")
    return {
        "arg_env_mapping": {"counter": "counter"},
        "next_function_to_call": "infinite_loop",
        "returned_values": {"counter": counter + 1}
    }

engine = IterativeRecursionEngine()
engine.add_function(infinite_loop)

try:
    engine.start_function_caller(
        next_function_to_call="infinite_loop",
        environment_variables={"counter": 0},
        arg_env_mapping={"counter": "counter"},
        max_iterations=10  # Safety limit
    )
except RuntimeError as e:
    print(f"Caught: {e}")
    # Output: Caught: Maximum iteration limit (10) reached...
```

## API Reference

### `IterativeRecursionEngine`

The main execution engine for iterative recursion.

#### Methods

##### `__init__()`
Creates a new engine instance.

```python
engine = IterativeRecursionEngine()
```

##### `add_function(function)`
Registers a function with the engine.

- **Parameters**: `function` - A callable that returns `FunctionReturn`
- **Returns**: None

```python
engine.add_function(my_function)
```

##### `register(function)`
Decorator to register a function with the engine. Alternative to `add_function()`.

- **Parameters**: `function` - A callable that returns `FunctionReturn`
- **Returns**: The same function (for chaining)

```python
@engine.register
def my_function(x: int) -> FunctionReturn:
    return {
        "arg_env_mapping": {},
        "next_function_to_call": None,
        "returned_values": {"result": x * 2}
    }
```

##### `add_environment_variables(variables: dict[str, Any])`
Adds or updates variables in the shared environment.

- **Parameters**: `variables` - Dictionary of variable names and values
- **Returns**: None

```python
engine.add_environment_variables({"x": 10, "y": 20})
```

##### `start_function_caller(next_function_to_call, environment_variables, arg_env_mapping, max_iterations=None)`
Begins executing functions starting from the specified function.

- **Parameters**:
  - `next_function_to_call` (str): Name of the first function to call
  - `environment_variables` (dict[str, Any]): Initial environment variables
  - `arg_env_mapping` (dict[str, str]): Parameter mapping for first function
  - `max_iterations` (int | None): Maximum iterations allowed (default: None/unlimited)
- **Returns**: `dict[str, Any]` - Final state of environment variables after execution
- **Raises**:
  - `KeyError`: If function not found or environment variable missing
  - `RuntimeError`: If `max_iterations` limit is reached
  - `ValueError`: If function returns invalid structure
  - `TypeError`: If function return has wrong types

```python
result = engine.start_function_caller(
    next_function_to_call="start_func",
    environment_variables={"value": 42},
    arg_env_mapping={"param": "value"},
    max_iterations=1000
)
# Access final state directly from result
print(result["some_value"])
```

#### Attributes

- `functions_dict` (dict): Registry of available functions
- `environment_variables` (dict): Shared state accessible to all functions

### Type Definitions

#### `FunctionReturn`
TypedDict defining the required return structure for functions.

```python
class FunctionReturn(TypedDict):
    arg_env_mapping: dict[str, str]
    next_function_to_call: str | None
    returned_values: dict[str, Any]
```

#### `VarsDict`
Type alias for variable dictionaries.

```python
VarsDict = dict[str, Any]
```

## Development

### Running Tests

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

### Test Coverage

The test suite includes:
- Basic function chaining
- Environment variable management
- Error handling and validation
- Runtime validation of return structures
- Iteration limits
- Decorator API (`@register`)
- Return value access
- Improved error messages
- Complex scenarios (factorial, state machines)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Carlos A. Planchón - [GitHub](https://github.com/carlosplanchon/iterativerecursion)

## Acknowledgments

This module was created as both a practical solution for deep recursion scenarios and an exploration of alternative execution patterns in Python.

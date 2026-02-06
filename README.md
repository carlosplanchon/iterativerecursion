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
    return FunctionReturn(
        returned_values={"next_name": "World"},
        next_function_to_call="farewell",
        arg_env_mapping={"name": "next_name"}
    )

def farewell(name: str) -> FunctionReturn:
    print(f"Goodbye, {name}!")
    return FunctionReturn(
        returned_values={}
        # next_function_to_call defaults to None to terminate
    )

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

Functions return a `FunctionReturn` dataclass instance with three attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `returned_values` | `dict[str, Any]` | Values to store in the shared environment |
| `next_function_to_call` | `str \| None` | Name of the next function to execute, or `None` to stop (default: `None`) |
| `arg_env_mapping` | `dict[str, str]` | Mapping of parameter names to environment variable keys (default: auto-mapped from `returned_values` keys) |

**Key Feature**: If `arg_env_mapping` is not specified, it automatically maps each key in `returned_values` to itself. For example, `{"counter": 5}` automatically creates `{"counter": "counter"}` mapping.

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
    return FunctionReturn(
        returned_values={"next_name": "World"},
        next_function_to_call="farewell",
        arg_env_mapping={"name": "next_name"}
    )

@engine.register
def farewell(name: str) -> FunctionReturn:
    print(f"Goodbye, {name}!")
    return FunctionReturn(
        returned_values={}
    )

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
        return FunctionReturn(
            returned_values={"result": accumulator}
        )
    # Auto-mapping: {"n": n-1, "accumulator": ...} automatically maps to itself
    return FunctionReturn(
        returned_values={
            "n": n - 1,
            "accumulator": accumulator * n
        },
        next_function_to_call="factorial_step"
    )

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
        return FunctionReturn(
            returned_values={"result": a}
        )
    # Auto-mapping handles {"n": "n", "a": "a", "b": "b"} automatically
    return FunctionReturn(
        returned_values={
            "n": n - 1,
            "a": b,
            "b": a + b
        },
        next_function_to_call="fibonacci"
    )

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
    # Auto-mapping: no need for {"counter": "counter"}
    return FunctionReturn(
        returned_values={"counter": counter + 1},
        next_function_to_call="infinite_loop"
    )

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
    return FunctionReturn(
        returned_values={"result": x * 2}
    )
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
Dataclass defining the required return structure for functions.

```python
@dataclass
class FunctionReturn:
    returned_values: dict[str, Any]
    next_function_to_call: str | None = None
    arg_env_mapping: dict[str, str] = field(default_factory=dict)
```

**Auto-mapping feature**: If `arg_env_mapping` is not provided, it automatically maps each key in `returned_values` to itself. This means you rarely need to specify `arg_env_mapping` explicitly.

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

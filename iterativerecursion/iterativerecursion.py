#!/usr/bin/env python3

from dataclasses import dataclass, field
from typing import Any, Callable

VarsDict = dict[str, Any]


@dataclass
class FunctionReturn:
    """
    Return type for functions executed by IterativeRecursionEngine.

    Attributes:
        returned_values: Dictionary of values to update in the environment.
        next_function_to_call: Name of the next function to execute, or None to
            terminate execution.
        arg_env_mapping: Mapping of parameter names to environment variable keys
            for the next function call. If not provided, automatically maps
            returned_values keys to themselves (e.g., {"x": 5} maps to {"x": "x"}).

    Example:
        # Simplest form - auto-mapping
        return FunctionReturn(
            returned_values={"counter": counter + 1},
            next_function_to_call="infinite_loop"
        )

        # Custom mapping when needed
        return FunctionReturn(
            returned_values={"result": 42},
            next_function_to_call="process",
            arg_env_mapping={"input": "result"}  # Maps param 'input' to env var 'result'
        )
    """
    returned_values: dict[str, Any]
    next_function_to_call: str | None = None
    arg_env_mapping: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Auto-populate arg_env_mapping if not provided."""
        if not self.arg_env_mapping:
            # Map each returned value key to itself
            self.arg_env_mapping = {k: k for k in self.returned_values.keys()}


class IterativeRecursionEngine:
    """
    Execute functions and "call" between them without recursion.

    You have a dict of variables on self.environment_variables that work as
    "global variables" inside of the executor.

    When you call a function, the values that return will update
    self.environment_variables, you pass only self.environment_variables
    as arguments to a function.
    """
    def __init__(self):
        self.functions_dict: dict[str, Callable[..., FunctionReturn]] = {}
        self.environment_variables: VarsDict = {}

    def _validate_function_return(self, resp: Any, func_name: str) -> None:
        """
        Validate function return is a FunctionReturn instance.

        :param resp: The return value from a function
        :param func_name: Name of the function that returned the value
        :raises TypeError: If return value is not a FunctionReturn instance
        """
        if not isinstance(resp, FunctionReturn):
            raise TypeError(
                f"Function '{func_name}' must return a FunctionReturn instance, "
                f"got {type(resp).__name__}. "
                f"Example: return FunctionReturn(returned_values={{'x': 5}}, next_function_to_call='next_func')"
            )

        # Validate types (dataclass doesn't enforce at runtime)
        if not isinstance(resp.arg_env_mapping, dict):
            raise TypeError(
                f"Function '{func_name}': arg_env_mapping must be dict, "
                f"got {type(resp.arg_env_mapping).__name__}"
            )

        if resp.next_function_to_call is not None and not isinstance(
            resp.next_function_to_call, str
        ):
            raise TypeError(
                f"Function '{func_name}': next_function_to_call must be str or None, "
                f"got {type(resp.next_function_to_call).__name__}"
            )

        if not isinstance(resp.returned_values, dict):
            raise TypeError(
                f"Function '{func_name}': returned_values must be dict, "
                f"got {type(resp.returned_values).__name__}"
            )

    def _resolve_arguments(
        self, arg_env_mapping: dict[str, str], func_name: str
    ) -> dict[str, Any]:
        """
        Resolve argument names to actual values from environment.

        :param arg_env_mapping: Mapping of parameter names to environment variable keys
        :param func_name: Name of the function (for error messages)
        :return: Dictionary mapping parameter names to actual values
        :raises KeyError: If required environment variables are missing
        """
        missing_vars = set(arg_env_mapping.values()) - self.environment_variables.keys()
        if missing_vars:
            available = set(self.environment_variables.keys())
            raise KeyError(
                f"Function '{func_name}' requires environment variables "
                f"that don't exist: {missing_vars}. "
                f"Available variables: {available if available else '(none)'}"
            )

        return {
            arg: self.environment_variables[env_key]
            for arg, env_key in arg_env_mapping.items()
        }

    def start_function_caller(
        self,
        next_function_to_call: str,
        environment_variables: VarsDict,
        arg_env_mapping: VarsDict,
        max_iterations: int | None = None
    ) -> VarsDict:
        """
        Start the execution of a function.

        :param next_function_to_call: What function to call first when starting
            this function. If next_function_to_call is None, this function stops
            and returns.
        :param environment_variables: Variables to add to the environment.
        :param arg_env_mapping: Arguments to call on the first function.
        :param max_iterations: Maximum number of function calls allowed before
            raising an error. None means unlimited iterations. Defaults to None.
        :return: The final state of environment_variables after execution completes
        :raises RuntimeError: If max_iterations limit is reached
        :raises KeyError: If function not found or environment variable missing
        :raises ValueError: If function returns invalid structure
        :raises TypeError: If function return has wrong types
        """
        if next_function_to_call is None:
            return self.environment_variables

        self.environment_variables.update(environment_variables)

        # Resolve initial arguments
        arg_env_mapping = self._resolve_arguments(arg_env_mapping, next_function_to_call)

        iteration_count = 0
        while True:
            # Check iteration limit
            if max_iterations is not None:
                if iteration_count >= max_iterations:
                    raise RuntimeError(
                        f"Maximum iteration limit ({max_iterations}) reached. "
                        f"This may indicate an infinite loop. "
                        f"Last function called: {next_function_to_call}"
                    )
                iteration_count += 1

            # Execute function
            resp = self.functions_dict[next_function_to_call](**arg_env_mapping)

            # Validate return structure
            self._validate_function_return(resp, next_function_to_call)

            # Update environment with returned values
            self.environment_variables.update(resp.returned_values)

            # Determine next function to call
            next_function_to_call = resp.next_function_to_call
            if not next_function_to_call:
                return self.environment_variables
            elif next_function_to_call not in self.functions_dict:
                available_funcs = set(self.functions_dict.keys())
                raise KeyError(
                    f"Function '{next_function_to_call}' not found in registry. "
                    f"Available functions: {available_funcs if available_funcs else '(none)'}"
                )

            # Resolve arguments for next function call
            arg_env_mapping = self._resolve_arguments(
                resp.arg_env_mapping, next_function_to_call
            )

    def add_environment_variables(self, environment_variables_dict_update: VarsDict):
        """
        Define new variables inside of the executor.

        :param environment_variables_dict_update: Dict of new variables to add.
        """
        self.environment_variables.update(environment_variables_dict_update)

    def add_function(self, function: Callable[..., FunctionReturn]) -> None:
        """
        Define new functions inside of the executor.

        :param function: Function to add. Must return FunctionReturn structure.
        """
        self.functions_dict[function.__name__] = function

    def register(self, func: Callable[..., FunctionReturn]) -> Callable[..., FunctionReturn]:
        """
        Decorator to register a function with the engine.

        Example:
            @engine.register
            def my_func(x: int) -> FunctionReturn:
                return FunctionReturn(
                    returned_values={"result": x * 2},
                    next_function_to_call=None
                )

        :param func: Function to register
        :return: The same function (for chaining)
        """
        self.add_function(func)
        return func

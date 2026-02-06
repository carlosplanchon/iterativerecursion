#!/usr/bin/env python3
"""
Tests for the IterativeRecursionEngine.
"""

import pytest
from iterativerecursion import (
    IterativeRecursionEngine,
    FunctionReturn,
    VarsDict
)


class TestBasicFunctionality:
    """Test basic function chaining and execution."""

    def test_simple_function_chain(self):
        """Test chaining two functions together."""
        results = []

        def func_1(a: int) -> FunctionReturn:
            results.append(f"func_1: {a}")
            return {
                "arg_env_mapping": {"b": "result_a"},
                "next_function_to_call": "func_2",
                "returned_values": {"result_a": a + 1}
            }

        def func_2(b: int) -> FunctionReturn:
            results.append(f"func_2: {b}")
            return {
                "arg_env_mapping": {},
                "next_function_to_call": None,
                "returned_values": {"result_b": b * 2}
            }

        executor = IterativeRecursionEngine()
        executor.add_function(func_1)
        executor.add_function(func_2)
        executor.start_function_caller(
            next_function_to_call="func_1",
            environment_variables={"initial": 5},
            arg_env_mapping={"a": "initial"}
        )

        assert results == ["func_1: 5", "func_2: 6"]
        assert executor.environment_variables["result_a"] == 6
        assert executor.environment_variables["result_b"] == 12

    def test_single_function_execution(self):
        """Test executing a single function that terminates immediately."""
        def simple_func(x: int) -> FunctionReturn:
            return {
                "arg_env_mapping": {},
                "next_function_to_call": None,
                "returned_values": {"output": x * 10}
            }

        executor = IterativeRecursionEngine()
        executor.add_function(simple_func)
        executor.start_function_caller(
            next_function_to_call="simple_func",
            environment_variables={"value": 7},
            arg_env_mapping={"x": "value"}
        )

        assert executor.environment_variables["output"] == 70

    def test_none_initial_function(self):
        """Test that starting with None terminates immediately."""
        executor = IterativeRecursionEngine()
        result = executor.start_function_caller(
            next_function_to_call=None,
            environment_variables={},
            arg_env_mapping={}
        )

        assert result == {}  # Returns empty environment dict


class TestEnvironmentVariables:
    """Test environment variable management."""

    def test_add_environment_variables(self):
        """Test adding environment variables."""
        executor = IterativeRecursionEngine()
        executor.add_environment_variables({"x": 10, "y": 20})

        assert executor.environment_variables["x"] == 10
        assert executor.environment_variables["y"] == 20

    def test_environment_variable_updates(self):
        """Test that returned values update the environment."""
        def updating_func(val: int) -> FunctionReturn:
            return {
                "arg_env_mapping": {},
                "next_function_to_call": None,
                "returned_values": {
                    "updated": val + 100,
                    "new_var": "created"
                }
            }

        executor = IterativeRecursionEngine()
        executor.add_function(updating_func)
        executor.start_function_caller(
            next_function_to_call="updating_func",
            environment_variables={"initial_val": 50},
            arg_env_mapping={"val": "initial_val"}
        )

        assert executor.environment_variables["updated"] == 150
        assert executor.environment_variables["new_var"] == "created"

    def test_environment_variable_persistence(self):
        """Test that environment variables persist across function calls."""
        def func_1(x: int) -> FunctionReturn:
            return {
                "arg_env_mapping": {"y": "stored_value"},
                "next_function_to_call": "func_2",
                "returned_values": {"stored_value": x * 2}
            }

        def func_2(y: int) -> FunctionReturn:
            return {
                "arg_env_mapping": {"z": "stored_value"},
                "next_function_to_call": "func_3",
                "returned_values": {"another_value": y + 10}
            }

        def func_3(z: int) -> FunctionReturn:
            return {
                "arg_env_mapping": {},
                "next_function_to_call": None,
                "returned_values": {"final": z + 1}
            }

        executor = IterativeRecursionEngine()
        executor.add_function(func_1)
        executor.add_function(func_2)
        executor.add_function(func_3)
        executor.start_function_caller(
            next_function_to_call="func_1",
            environment_variables={"input": 5},
            arg_env_mapping={"x": "input"}
        )

        assert executor.environment_variables["stored_value"] == 10
        assert executor.environment_variables["another_value"] == 20
        assert executor.environment_variables["final"] == 11


class TestErrorHandling:
    """Test error handling and validation."""

    def test_missing_function_error(self):
        """Test that calling a non-existent function raises KeyError."""
        def bad_func(x: int) -> FunctionReturn:
            return {
                "arg_env_mapping": {},
                "next_function_to_call": "nonexistent_function",
                "returned_values": {}
            }

        executor = IterativeRecursionEngine()
        executor.add_function(bad_func)

        with pytest.raises(KeyError, match="nonexistent_function"):
            executor.start_function_caller(
                next_function_to_call="bad_func",
                environment_variables={"val": 1},
                arg_env_mapping={"x": "val"}
            )

    def test_missing_environment_variable_error(self):
        """Test that referencing non-existent environment variables raises KeyError."""
        def func_with_bad_args(x: int) -> FunctionReturn:
            return {
                "arg_env_mapping": {"y": "nonexistent_var"},
                "next_function_to_call": "another_func",
                "returned_values": {}
            }

        def another_func(y: int) -> FunctionReturn:
            return {
                "arg_env_mapping": {},
                "next_function_to_call": None,
                "returned_values": {}
            }

        executor = IterativeRecursionEngine()
        executor.add_function(func_with_bad_args)
        executor.add_function(another_func)

        with pytest.raises(KeyError, match="requires environment variables that don't exist"):
            executor.start_function_caller(
                next_function_to_call="func_with_bad_args",
                environment_variables={"val": 1},
                arg_env_mapping={"x": "val"}
            )


class TestIterationLimit:
    """Test iteration limit safety feature."""

    def test_iteration_limit_prevents_infinite_loop(self):
        """Test that max_iterations prevents infinite loops."""
        def infinite_func(counter: int) -> FunctionReturn:
            return {
                "arg_env_mapping": {"counter": "counter"},
                "next_function_to_call": "infinite_func",
                "returned_values": {"counter": counter + 1}
            }

        executor = IterativeRecursionEngine()
        executor.add_function(infinite_func)

        with pytest.raises(RuntimeError, match="Maximum iteration limit.*reached"):
            executor.start_function_caller(
                next_function_to_call="infinite_func",
                environment_variables={"counter": 0},
                arg_env_mapping={"counter": "counter"},
                max_iterations=100
            )

    def test_iteration_limit_allows_valid_chains(self):
        """Test that iteration limit doesn't interfere with valid execution."""
        call_count = 0

        def counting_func(n: int) -> FunctionReturn:
            nonlocal call_count
            call_count += 1
            if n > 0:
                return {
                    "arg_env_mapping": {"n": "n"},
                    "next_function_to_call": "counting_func",
                    "returned_values": {"n": n - 1}
                }
            else:
                return {
                    "arg_env_mapping": {},
                    "next_function_to_call": None,
                    "returned_values": {"done": True}
                }

        executor = IterativeRecursionEngine()
        executor.add_function(counting_func)
        executor.start_function_caller(
            next_function_to_call="counting_func",
            environment_variables={"n": 10},
            arg_env_mapping={"n": "n"},
            max_iterations=20
        )

        assert call_count == 11  # Calls for n=10, 9, 8, ..., 1, 0
        assert executor.environment_variables["done"] is True

    def test_no_iteration_limit_by_default(self):
        """Test that unlimited iterations work when max_iterations is None."""
        def recursive_countdown(n: int) -> FunctionReturn:
            if n > 0:
                return {
                    "arg_env_mapping": {"n": "n"},
                    "next_function_to_call": "recursive_countdown",
                    "returned_values": {"n": n - 1}
                }
            else:
                return {
                    "arg_env_mapping": {},
                    "next_function_to_call": None,
                    "returned_values": {"result": "done"}
                }

        executor = IterativeRecursionEngine()
        executor.add_function(recursive_countdown)
        executor.start_function_caller(
            next_function_to_call="recursive_countdown",
            environment_variables={"n": 1000},
            arg_env_mapping={"n": "n"}
            # No max_iterations specified
        )

        assert executor.environment_variables["result"] == "done"


class TestComplexScenarios:
    """Test more complex usage scenarios."""

    def test_factorial_like_computation(self):
        """Test a factorial-like computation using the engine."""
        def factorial_step(n: int, accumulator: int) -> FunctionReturn:
            if n <= 1:
                return {
                    "arg_env_mapping": {},
                    "next_function_to_call": None,
                    "returned_values": {"result": accumulator}
                }
            else:
                return {
                    "arg_env_mapping": {
                        "n": "n",
                        "accumulator": "accumulator"
                    },
                    "next_function_to_call": "factorial_step",
                    "returned_values": {
                        "n": n - 1,
                        "accumulator": accumulator * n
                    }
                }

        executor = IterativeRecursionEngine()
        executor.add_function(factorial_step)
        executor.start_function_caller(
            next_function_to_call="factorial_step",
            environment_variables={"n": 5, "accumulator": 1},
            arg_env_mapping={"n": "n", "accumulator": "accumulator"}
        )

        assert executor.environment_variables["result"] == 120  # 5!

    def test_state_machine_simulation(self):
        """Test simulating a simple state machine."""
        states_visited = []

        def state_a(value: int) -> FunctionReturn:
            states_visited.append("A")
            if value < 10:
                return {
                    "arg_env_mapping": {"value": "value"},
                    "next_function_to_call": "state_b",
                    "returned_values": {"value": value + 1}
                }
            else:
                return {
                    "arg_env_mapping": {},
                    "next_function_to_call": None,
                    "returned_values": {"final_value": value}
                }

        def state_b(value: int) -> FunctionReturn:
            states_visited.append("B")
            return {
                "arg_env_mapping": {"value": "value"},
                "next_function_to_call": "state_c",
                "returned_values": {"value": value + 2}
            }

        def state_c(value: int) -> FunctionReturn:
            states_visited.append("C")
            return {
                "arg_env_mapping": {"value": "value"},
                "next_function_to_call": "state_a",
                "returned_values": {"value": value + 1}
            }

        executor = IterativeRecursionEngine()
        executor.add_function(state_a)
        executor.add_function(state_b)
        executor.add_function(state_c)
        executor.start_function_caller(
            next_function_to_call="state_a",
            environment_variables={"value": 0},
            arg_env_mapping={"value": "value"},
            max_iterations=50
        )

        assert "A" in states_visited
        assert "B" in states_visited
        assert "C" in states_visited
        assert states_visited[0] == "A"
        assert executor.environment_variables["final_value"] >= 10


class TestRuntimeValidation:
    """Test runtime validation of function returns."""

    def test_missing_keys_in_return(self):
        """Test that missing keys in function return raises ValueError."""
        def bad_func(x: int):
            return {"arg_env_mapping": {}}  # Missing required keys

        executor = IterativeRecursionEngine()
        executor.add_function(bad_func)

        with pytest.raises(ValueError, match="returned invalid structure"):
            executor.start_function_caller(
                next_function_to_call="bad_func",
                environment_variables={"val": 1},
                arg_env_mapping={"x": "val"}
            )

    def test_wrong_type_for_arg_env_mapping(self):
        """Test that wrong type for arg_env_mapping raises TypeError."""
        def bad_func(x: int) -> FunctionReturn:
            return {
                "arg_env_mapping": "not a dict",  # Wrong type
                "next_function_to_call": None,
                "returned_values": {}
            }

        executor = IterativeRecursionEngine()
        executor.add_function(bad_func)

        with pytest.raises(TypeError, match="arg_env_mapping must be dict"):
            executor.start_function_caller(
                next_function_to_call="bad_func",
                environment_variables={"val": 1},
                arg_env_mapping={"x": "val"}
            )

    def test_wrong_type_for_next_function_to_call(self):
        """Test that wrong type for next_function_to_call raises TypeError."""
        def bad_func(x: int) -> FunctionReturn:
            return {
                "arg_env_mapping": {},
                "next_function_to_call": 123,  # Wrong type
                "returned_values": {}
            }

        executor = IterativeRecursionEngine()
        executor.add_function(bad_func)

        with pytest.raises(TypeError, match="next_function_to_call must be str or None"):
            executor.start_function_caller(
                next_function_to_call="bad_func",
                environment_variables={"val": 1},
                arg_env_mapping={"x": "val"}
            )

    def test_wrong_type_for_returned_values(self):
        """Test that wrong type for returned_values raises TypeError."""
        def bad_func(x: int) -> FunctionReturn:
            return {
                "arg_env_mapping": {},
                "next_function_to_call": None,
                "returned_values": "not a dict"  # Wrong type
            }

        executor = IterativeRecursionEngine()
        executor.add_function(bad_func)

        with pytest.raises(TypeError, match="returned_values must be dict"):
            executor.start_function_caller(
                next_function_to_call="bad_func",
                environment_variables={"val": 1},
                arg_env_mapping={"x": "val"}
            )

    def test_non_dict_return(self):
        """Test that returning non-dict raises TypeError."""
        def bad_func(x: int):
            return "not a dict"

        executor = IterativeRecursionEngine()
        executor.add_function(bad_func)

        with pytest.raises(TypeError, match="must return a dict"):
            executor.start_function_caller(
                next_function_to_call="bad_func",
                environment_variables={"val": 1},
                arg_env_mapping={"x": "val"}
            )


class TestDecoratorAPI:
    """Test the @register decorator."""

    def test_register_decorator(self):
        """Test that @register decorator works correctly."""
        executor = IterativeRecursionEngine()

        @executor.register
        def decorated_func(x: int) -> FunctionReturn:
            return {
                "arg_env_mapping": {},
                "next_function_to_call": None,
                "returned_values": {"result": x * 3}
            }

        # Verify function was registered
        assert "decorated_func" in executor.functions_dict

        # Verify it executes correctly
        result = executor.start_function_caller(
            next_function_to_call="decorated_func",
            environment_variables={"value": 5},
            arg_env_mapping={"x": "value"}
        )

        assert result["result"] == 15

    def test_register_decorator_with_chaining(self):
        """Test that @register allows function chaining."""
        executor = IterativeRecursionEngine()

        @executor.register
        def first_func(x: int) -> FunctionReturn:
            return {
                "arg_env_mapping": {"y": "intermediate"},
                "next_function_to_call": "second_func",
                "returned_values": {"intermediate": x + 10}
            }

        @executor.register
        def second_func(y: int) -> FunctionReturn:
            return {
                "arg_env_mapping": {},
                "next_function_to_call": None,
                "returned_values": {"final": y * 2}
            }

        result = executor.start_function_caller(
            next_function_to_call="first_func",
            environment_variables={"start": 5},
            arg_env_mapping={"x": "start"}
        )

        assert result["final"] == 30  # (5 + 10) * 2


class TestReturnValueAccess:
    """Test improved return value access."""

    def test_return_value_access(self):
        """Test that start_function_caller returns final environment."""
        def simple_func(x: int) -> FunctionReturn:
            return {
                "arg_env_mapping": {},
                "next_function_to_call": None,
                "returned_values": {"computed": x * 100}
            }

        executor = IterativeRecursionEngine()
        executor.add_function(simple_func)

        result = executor.start_function_caller(
            next_function_to_call="simple_func",
            environment_variables={"input": 7},
            arg_env_mapping={"x": "input"}
        )

        # Can access result directly from return value
        assert result["computed"] == 700
        # Also still available in environment
        assert executor.environment_variables["computed"] == 700

    def test_return_preserves_initial_variables(self):
        """Test that returned dict includes initial environment variables."""
        def noop_func(x: int) -> FunctionReturn:
            return {
                "arg_env_mapping": {},
                "next_function_to_call": None,
                "returned_values": {}
            }

        executor = IterativeRecursionEngine()
        executor.add_function(noop_func)

        result = executor.start_function_caller(
            next_function_to_call="noop_func",
            environment_variables={"preserve_me": 42},
            arg_env_mapping={"x": "preserve_me"}
        )

        assert result["preserve_me"] == 42


class TestImprovedErrorMessages:
    """Test improved error messages."""

    def test_missing_function_error_message(self):
        """Test that missing function error shows available functions."""
        def func(x: int) -> FunctionReturn:
            return {
                "arg_env_mapping": {},
                "next_function_to_call": "nonexistent",
                "returned_values": {}
            }

        executor = IterativeRecursionEngine()
        executor.add_function(func)

        with pytest.raises(KeyError, match="not found in registry"):
            executor.start_function_caller(
                next_function_to_call="func",
                environment_variables={"val": 1},
                arg_env_mapping={"x": "val"}
            )

    def test_missing_env_var_error_shows_available(self):
        """Test that missing env var error shows what's available."""
        def func1(x: int) -> FunctionReturn:
            return {
                "arg_env_mapping": {"y": "missing_var"},
                "next_function_to_call": "func2",
                "returned_values": {"existing_var": 10}
            }

        def func2(y: int) -> FunctionReturn:
            return {
                "arg_env_mapping": {},
                "next_function_to_call": None,
                "returned_values": {}
            }

        executor = IterativeRecursionEngine()
        executor.add_function(func1)
        executor.add_function(func2)

        with pytest.raises(KeyError, match="Available variables"):
            executor.start_function_caller(
                next_function_to_call="func1",
                environment_variables={"val": 1},
                arg_env_mapping={"x": "val"}
            )

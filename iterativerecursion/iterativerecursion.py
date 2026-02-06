#!/usr/bin/env python3

from typing import Any, Union

VarsDict = dict[str, Any]
FunctionReturn = dict[str, Union[dict, str | None]]


class IterativeRecursionEngine:
    """
    Execute functions and "call" between them without recursion.

    You have a dict of variables on self.enviroment_variables that work as
    "global variables" inside of the executor.

    When you call a function, the values that return will update
    self.enviroment_variables, you pass only self.enviroment_variables
    as arguments to a function.
    """
    def __init__(self):
        self.functions_dict: dict[Any, Any] = dict()
        self.enviroment_variables: VarsDict = dict()

    def start_function_caller(
        self,
        next_function_to_call: str,
        enviroment_variables: VarsDict,
        call_arg_n_func: VarsDict
            ) -> None:
        """
        Start the execution of a function.
        :param next_function_to_call: str: What function to call first
            when starting this function. If next_function_to_call is None
            this function stop and return.
        :param enviroment_variables: VarsDict: Variables to add
            on the enviroment.
        :param call_arg_n_func: VarsDict: Arguments to call on
            the first function.

        """
        if next_function_to_call is None:
            return None

        self.enviroment_variables.update(enviroment_variables)

        for arg in call_arg_n_func:
            call_arg_n_func[arg] = self.enviroment_variables[
                    call_arg_n_func[arg]
                ]

        while True:
            resp = self.functions_dict[
                    next_function_to_call
                ](**call_arg_n_func)
            # We update our enviroment parameters.
            self.enviroment_variables.update(resp["returned_values"])

            next_function_to_call = resp["next_function_to_call"]
            if not next_function_to_call:
                return None
            elif next_function_to_call not in self.functions_dict:
                raise KeyError(
                        f"Function {next_function_to_call} "
                        "not in self.functions_dict and not None"
                    )

            call_arg_n_func = resp["call_arg_n_func"]
            if not set(
                call_arg_n_func.values()
                    ).issubset(
                        self.enviroment_variables
                        ):
                raise KeyError(
                    "set(call_arg_n_func.values())"
                    "is not a subset of self.enviroment_variables"
                    )

            for arg in call_arg_n_func:
                call_arg_n_func[arg] = self.enviroment_variables[
                        call_arg_n_func[arg]
                    ]

    def add_enviroment_variables(
        self, enviroment_variables_dict_update: VarsDict
            ):
        """
        Define new variables inside of the executor.
        :param enviroment_variables_dict_update: VarsDict:
            Dict of new variables.
        to add.
        """
        self.enviroment_variables.update(enviroment_variables_dict_update)

    def add_function(self, function) -> None:
        """
        Define new functions inside of the executor.
        :param function: Function to add.

        """
        self.functions_dict[function.__name__] = function

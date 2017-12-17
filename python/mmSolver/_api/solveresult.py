"""
The information returned from a solve.

TODO: Write the entire class.
"""


class SolveResult(object):
    """
    The information returned from a solve.

    We should have all information from the solver, we can then query it as
    needed. This class should never modify data, it only stores data.
    """
    def __init__(self, data):
        assert isinstance(data, list)
        self._data = {}

        # Python API data
        self._collection_name = None
        self._solver = None  # expected to be a copy of the used Solver class.
        self._marker_list = []  # markers

        # This is the data that the SolveResult will contain from the 'mmSolver'
        # command. We must extract it and each variable...

        for d in data:
            assert isinstance(d, (str, unicode))
            splt = d.partition('=')
            key = splt[0]
            value = splt[-1]
            if not key:
                continue
            self._data[key] = value

        # Command Success or not? Did the solver fail?
        self._success = None

        # Parameter Results
        # TODO: List the solved parameters, the frame numbers and values.
        self._parameters = None

        # Errors
        # TODO: Create a list of errors, per-marker, per-frame, so we can
        # allowing graph the errors and detecting problems.
        self._per_frame_error = None

        # Termination Reason
        self._termination_reason_num = None
        self._termination_reason_str = None

        # Iterations
        self._iterations = None
        self._function_evaluations = None
        self._jacobian_evaluations = None
        self._attempts_for_reducing_error = None

        # Timer data
        self._timer_solve_sec = None
        self._timer_solve_tick = None
        self._timer_function_sec = None
        self._timer_function_tick = None
        self._timer_parameter_sec = None
        self._timer_parameter_tick = None
        self._timer_measure_sec = None
        self._timer_measure_tick = None
        self._timer_jacobian_sec = None
        self._timer_jacobian_tick = None

    def get_collection_name(self):
        return self._data.get('collection_name')

    def get_solver(self):
        return self._data.get('solver_type')

    def get_success(self):
        return self._data.get('success')

    def get_initial_error(self):
        return self._data.get('error_initial')

    def get_final_error(self):
        return self._data.get('error_final')

    def get_final_avg_error(self):
        return self._data.get('error_final_average')

    def get_final_max_error(self):
        return self._data.get('error_final_maximum')

    def get_final_min_error(self):
        return self._data.get('error_final_minimum')

    # def get_per_frame_error(self):
    #     pass

    def get_reason_for_stopping(self):
        return self._data.get('reason_string')

    def get_iterations(self):
        return self._data.get('iteration_num')

    def get_function_iterations(self):
        return self._data.get('iteration_function_num')

    def get_jacobian_iterations(self):
        return self._data.get('iteration_jacobian_num')

    def get_iteration_attempts(self):
        return self._data.get('iteration_attempt_num')
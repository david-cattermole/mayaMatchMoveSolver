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

        # Python API data
        self._collection_name = None
        self._solver = None  # expected to be a copy of the used Solver class.
        self._marker_list = []  # markers

        # This is the data that the SolveResult will contain from the 'mmSolver'
        # command. We must extract it and each variable...

        # Command Success or not? Did the solver fail?
        self._success = None

        # Parameter Results
        # TODO: List the solved parameters, the frame numbers and values.
        self._parameters = None

        # Errors
        self._initial_error = None
        self._final_error = None
        self._average_error = None
        self._max_error = None
        self._min_error = None
        self._jt_error = None
        self._dp_error = None
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
        pass

    def get_solver(self):
        pass

    def get_success(self):
        return self._success

    def get_error(self):
        return self._final_error

    def get_per_frame_error(self):
        pass

    def get_reason_for_stopping(self):
        pass

    def get_max_iterations(self):
        pass

"""
Solver related functions.
"""


SOLVER_TYPE_LEVMAR = 0
SOLVER_TYPE_SPLM = 1


class Solver(object):
    """
    Solver; the options for how a solver should be executed.
    """
    def __init__(self, data=None):
        self._data = {}
        if isinstance(data, dict):
            self.set_data(data)

    def get_data(self):
        assert isinstance(self._data, dict)
        return self._data.copy()

    def set_data(self, data):
        assert isinstance(data, dict)
        self._data = data.copy()
        return self

    ############################################################################

    def get_max_iterations(self):
        return self._data.get('max_iterations')

    def set_max_iterations(self, value):
        self._data['max_iterations'] = value
        return

    def get_solver_type(self):
        pass

    def set_solver_type(self, value):
        pass

    def get_verbose(self):
        pass

    def set_verbose(self, value):
        pass

    def add_frame(self, value):
        pass

    def set_frame_list(self, value_list):
        pass

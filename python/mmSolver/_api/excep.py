"""
Module of exceptions for the entire mmSolver API.
"""


class MMException(Exception):
    """
    Base class for all mmSolver exceptions.
    """
    pass


class NotValid(MMException):
    """
    Raised when an object is not valid.
    """
    pass


class AlreadyLinked(MMException):
    """
    Raised when two objects are already connected (linked).
    """
    pass


class AlreadyUnlinked(MMException):
    """
    Raised when two objects are already disconnected (unlinked).
    """
    pass


class NotEnoughMarkers(MMException):
    """
    There are too many Attribute values in the solver for the Markers given.
    """
    pass


class SolverNotAvailable(MMException):
    """
    Raised when the mmSolver cannot be used (because the plug-in isn't loaded).
    """
    pass

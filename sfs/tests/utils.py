import functools

from sfs.spaces import ConstraintSpace, GeneralObjectSpace, TypeSpace


def needs_spaces(func):
    @functools.wraps(func)
    def wrapper(test_case):
        cos = ConstraintSpace()
        tys = TypeSpace(test_case.graph)
        obs = GeneralObjectSpace(test_case.graph)
        return func(test_case, cos, tys, obs)
    return wrapper

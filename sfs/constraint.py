from enum import Enum


class CompositeOperation(Enum):
    intersection = 0
    union = 1


class Constraint(object):
    def __and__(self, other):
        return CompositeConstraint(CompositeOperation.intersection,
                                   self, other)

    def __or__(self, other):
        return CompositeConstraint(CompositeOperation.union,
                                   self, other)


class CompositeConstraint(Constraint):
    def __init__(self, operation, *operands):
        self.operation = operation
        self.operands = operands


class AbnormalArgument(Enum):
    Unspecified = 0


class PrimitiveConstraint(Constraint):
    def __init__(self,
                 predicate,
                 obj=AbnormalArgument.Unspecified,
                 subj=AbnormalArgument.Unspecified):
        self.predicate = predicate
        self.obj = obj
        self.subj = subj
        # Exactly one must be spcified
        assert (obj != AbnormalArgument.Unspecified) ^ (subj != AbnormalArgument.Unspecified)

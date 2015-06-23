from sfs.constraint import (AbnormalArgument,
                            CompositeOperation,
                            IndirectConstraint,
                            PrimitiveConstraint)


class Traverser(object):
    def __init__(self, rdfgraph):
        self.rdfgraph = rdfgraph

    def getall(self, constraint):
        if isinstance(constraint, PrimitiveConstraint):
            if constraint.obj == AbnormalArgument.Unspecified:
                return set(self.rdfgraph.objects(constraint.subj, constraint.predicate))
            else:
                return set(self.rdfgraph.subjects(constraint.predicate, constraint.obj))
        if isinstance(constraint, IndirectConstraint):
            if constraint.subj_constraint == AbnormalArgument.Unspecified:
                sub_satisfiers = self.getall(constraint.obj_constraint)
                sub_constraints = [PrimitiveConstraint(constraint.predicate, sub_satisfier)
                                   for sub_satisfier in sub_satisfiers]
                return set().union(*map(self.getall, sub_constraints))
            else:
                raise NotImplementedError
        operands = list(map(self.getall, constraint.operands))
        if constraint.operation == CompositeOperation.intersection:
            return set.intersection(*operands)
        else:
            return set.union(*operands)

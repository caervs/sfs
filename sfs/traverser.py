from sfs.constraint import (AbnormalArgument,
                            CompositeOperation,
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

        operands = map(self.getall, constraint.operands)
        if constraint.operation == CompositeOperation.intersection:
            return set.intersection(*operands)
        else:
            return set.union(*operands)

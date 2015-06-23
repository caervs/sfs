class ConstraintSpace(object):
    def __getattr__(self, attr_name):
        return functools.partial(PrimitiveConstraint, getattr(FOAF, attr_name))


class ObjectSpace(object):
    def __init__(self, graph, type_name):
        self.type_name = type_name
        self.graph = graph

    def __iter__(self):
        return self.graph.subjects(FOAF.isa, getattr(FOAF, self.type_name))

    def __getattr__(self, attr_name):
        attr_name = attr_name.lower()
        for subj in self:
            if (subj, FOAF.hasname, Literal(attr_name)) in self.graph:
                return subj
        raise KeyError(attr_name)


class TypeSpace(object):
    def __init__(self, graph):
        self.graph = graph

    def __getattr__(self, attr_name):
        check_triple = (getattr(FOAF, type_name),
                        FOAF.isa,
                        getattr(FOAF, "typename"))
        if check_triple in self.graph:
            return getattr(FOAF, attr_name)

        if attr_name.endswith("s"):
            return ObjectSpace(self.graph, attr_name[:-1])
        
        raise AttributeError(attr_name)

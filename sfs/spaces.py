import functools

from rdflib import Literal
from rdflib.namespace import FOAF

from sfs.constraint import (AbnormalArgument, IndirectConstraint,
                            PrimitiveConstraint)


class ConstraintCreator(object):
    def __init__(self, predicate):
        self.predicate = predicate

    def __call__(self,
                 obj=AbnormalArgument.Unspecified,
                 subj=AbnormalArgument.Unspecified):
        return PrimitiveConstraint(self.predicate, obj, subj)

    def __mul__(self, constraint):
        return IndirectConstraint(self.predicate, constraint)

class ConstraintSpace(object):
    def __getattr__(self, attr_name):
        return ConstraintCreator(getattr(FOAF, attr_name))


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
        raise AttributeError(attr_name)


class GeneralObjectSpace(object):
    def __init__(self, graph):
        self.graph = graph

    def __getattr__(self, obj_name):
        subjects = list(self.graph.subjects(FOAF.hasname, Literal(obj_name)))
        if len(subjects) != 1:
            raise AttributeError(obj_name, len(subjects))
        return subjects[0]


class TypeSpace(object):
    def __init__(self, graph):
        self.graph = graph

    def __getattr__(self, attr_name):
        check_triple = (Literal(attr_name),
                        FOAF.isa, FOAF.typename)
        if check_triple in self.graph:
            return getattr(FOAF, attr_name)

        if attr_name.endswith("s"):
            return ObjectSpace(self.graph, attr_name[:-1])
        
        raise AttributeError(attr_name)

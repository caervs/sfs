import unittest

from rdflib import BNode, Graph, Literal
from rdflib.namespace import FOAF

from sfs.traverser import Traverser
from sfs.spaces import ConstraintSpace, TypeSpace


class TraverserTestCase(unittest.TestCase):
    pass


class BasicInteractionWorks(TraverserTestCase):
    graph_structure = {
        'elems': {
            "Person": ['rhea', 'jason'],
            "Photo": ['photo', 'photo2', 'photo3']
        },
        'statements': [
            ('photo', 'features', 'rhea'),
            ('photo2', 'features', 'jason'),
            ('photo3', 'features', 'rhea'),
            ('photo3', 'features', 'jason'),
        ]
    }

    def setUp(self):
        self.graph = Graph()
        self.types_by_name = {}
        self.objects_by_name = {}

        for obj_type_name, obj_names in self.graph_structure['elems'].items():
            self.graph.add((Literal(obj_type_name), FOAF.isa, FOAF.typename))

            obj_type = getattr(FOAF, obj_type_name)
            self.types_by_name[obj_type_name] = obj_type

            for obj_name in obj_names:
                node = BNode(obj_name)
                self.objects_by_name[obj_name] = node
                self.graph.add((node, FOAF.isa, obj_type))
                self.graph.add((node, FOAF.hasname, Literal(obj_name)))

        for subj_name, pred_name, obj_name in self.graph_structure['statements']:
            self.graph.add((self.objects_by_name[subj_name],
                            getattr(FOAF, pred_name),
                            self.objects_by_name[obj_name]))
        self.traverser = Traverser(self.graph)

    def assert_have_titles(self, nodes, titles):
        node_titles = set(node.title() for node in nodes)
        self.assertEqual(node_titles, set(titles))

    def test_get_rhea_photos(self):
        cos = ConstraintSpace()
        tys = TypeSpace(self.graph)
        constraint = cos.isa(tys.Photo) & cos.features(tys.Persons.Rhea)
        photos = self.traverser.getall(constraint)
        self.assert_have_titles(photos, ["Photo", "Photo3"])

    def test_get_jason_photos(self):
        cos = ConstraintSpace()
        tys = TypeSpace(self.graph)
        constraint = cos.isa(tys.Photo) & cos.features(tys.Persons.Jason)
        photos = self.traverser.getall(constraint)
        self.assert_have_titles(photos, ["Photo2", "Photo3"])

    def test_get_both_photos(self):
        cos = ConstraintSpace()
        tys = TypeSpace(self.graph)
        constraint = (cos.isa(tys.Photo) & cos.features(tys.Persons.Jason)
                      & cos.features(tys.Persons.Rhea))
        photos = self.traverser.getall(constraint)
        self.assert_have_titles(photos, ["Photo3"])

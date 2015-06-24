import unittest

from rdflib import BNode, Graph, Literal
from rdflib.namespace import FOAF

from sfs.tests.utils import needs_spaces
from sfs.traverser import Traverser


class TraverserTestCase(unittest.TestCase):
    pass


class BasicInteractionWorks(TraverserTestCase):
    graph_structure = {
        'elems': {
            ("Person", "Girl"): ['rhea', 'roxanne'],
            ("Person", "Boy"): ['jason'],
            ("Photo",): ['photo', 'photo2', 'photo3']
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

        for obj_type_names, obj_names in self.graph_structure['elems'].items():
            obj_types = []
            for obj_type_name in obj_type_names:
                self.graph.add((Literal(obj_type_name), FOAF.isa, FOAF.typename))

                obj_type = getattr(FOAF, obj_type_name)
                self.types_by_name[obj_type_name] = obj_type
                obj_types.append(obj_type)

            for obj_name in obj_names:
                node = BNode(obj_name)
                self.objects_by_name[obj_name] = node
                for obj_type in obj_types:
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

    @needs_spaces
    def test_get_rhea_photos(self, cos, tys, _obs):
        constraint = cos.isa(tys.Photo) & cos.features(tys.Persons.Rhea)
        photos = self.traverser.getall(constraint)
        self.assert_have_titles(photos, ["Photo", "Photo3"])

    @needs_spaces
    def test_get_jason_photos(self, cos, tys, _obs):
        constraint = cos.isa(tys.Photo) & cos.features(tys.Persons.Jason)
        photos = self.traverser.getall(constraint)
        self.assert_have_titles(photos, ["Photo2", "Photo3"])

    @needs_spaces
    def test_get_compound(self, cos, tys, _obs):
        constraint = (cos.isa(tys.Photo) & cos.features(tys.Persons.Jason)
                      & cos.features(tys.Persons.Rhea))
        photos = self.traverser.getall(constraint)
        self.assert_have_titles(photos, ["Photo3"])

    @needs_spaces
    def test_get_indirect(self, cos, tys, _obs):
        constraint = (cos.isa(tys.Photo) &
                      (cos.features * cos.isa(tys.Girl)))

        photos = self.traverser.getall(constraint)
        self.assert_have_titles(photos, ["Photo", "Photo3"])

    @needs_spaces
    def test_get_indirect_compound(self, cos, tys, _obs):
        constraint = (cos.isa(tys.Photo) &
                      cos.features(tys.Persons.jason) &
                      (cos.features * cos.isa(tys.Girl)))

        photos = self.traverser.getall(constraint)
        self.assert_have_titles(photos, ["Photo3"])

    @needs_spaces
    def test_general_object_space(self, cos, tys, obs):
        constraint = (cos.isa(tys.Photo) &
                      cos.features(obs.jason) &
                      (cos.features * cos.isa(tys.Girl)))

        photos = self.traverser.getall(constraint)
        self.assert_have_titles(photos, ["Photo3"])

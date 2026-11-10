import sys
import unittest
import itertools
import math
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import networkx as nx
from superfamilies import MOTIFS, count_graphlets, random_degree_preserving, analyze

class TestGraphlets(unittest.TestCase):
    def test_all_six(self):
        graphs = {
            'P4': nx.path_graph(4),
            'K1_3': nx.star_graph(3),
            'C4': nx.cycle_graph(4),
            'paw': nx.Graph([(0,1),(1,2),(2,0),(2,3)]),
            'diamond': nx.complete_graph(4),
            'K4': nx.complete_graph(4),
        }
        graphs['diamond'].remove_edge(0,1)
        for expected, graph in graphs.items():
            with self.subTest(expected=expected):
                counts = count_graphlets(graph)
                self.assertEqual(counts[expected], 1)
                self.assertEqual(sum(counts.values()), 1)
    def test_disconnected(self):
        self.assertEqual(sum(count_graphlets(nx.empty_graph(6)).values()), 0)
    def test_degree_preservation(self):
        graph = nx.karate_club_graph()
        shuffled = random_degree_preserving(graph, 1)
        self.assertEqual(dict(graph.degree()), dict(shuffled.degree()))
    def test_profile(self):
        result = analyze(nx.path_graph(6), repetitions=2)
        self.assertEqual(set(result['srp']), set(MOTIFS))
        self.assertIn(round(sum(x*x for x in result['srp'].values()), 6), (0.0, 1.0))

    def test_atlas_against_brute_force(self):
        # All 1,253 unlabeled simple graphs with at most seven vertices.
        templates = {name: graph for name, graph in zip(MOTIFS, [
            nx.path_graph(4), nx.star_graph(3), nx.cycle_graph(4),
            nx.Graph([(0, 1), (1, 2), (2, 0), (2, 3)]),
            nx.complete_graph(4), nx.complete_graph(4)])}
        templates['diamond'].remove_edge(0, 1)
        for graph in nx.graph_atlas_g():
            expected = dict.fromkeys(MOTIFS, 0)
            for nodes in itertools.combinations(graph, 4):
                subgraph = graph.subgraph(nodes)
                if nx.is_connected(subgraph):
                    name = next(k for k, template in templates.items()
                                if nx.is_isomorphic(subgraph, template))
                    expected[name] += 1
            self.assertEqual(count_graphlets(graph), expected)

    def test_ratio_formula(self):
        graph = nx.path_graph(4)
        with patch('superfamilies.random_degree_preserving',
                   return_value=nx.cycle_graph(4)) as randomize:
            randomize.return_value.graph['swap_target_reached'] = True
            result = analyze(graph, repetitions=2)
        self.assertAlmostEqual(result['delta']['P4'], 1 / 5)
        self.assertAlmostEqual(result['delta']['C4'], -1 / 5)
        self.assertAlmostEqual(result['srp']['P4'], 1 / math.sqrt(2))
        self.assertAlmostEqual(result['srp']['C4'], -1 / math.sqrt(2))

    def test_reproducibility(self):
        self.assertEqual(analyze(nx.karate_club_graph(), repetitions=3),
                         analyze(nx.karate_club_graph(), repetitions=3))

    def test_invalid_parameters(self):
        for kwargs in ({'repetitions': 0}, {'epsilon': 0}, {'swap_multiplier': -1}):
            with self.assertRaises(ValueError):
                analyze(nx.path_graph(6), **kwargs)

    def test_input_unchanged(self):
        graph = nx.karate_club_graph()
        edges = set(graph.edges())
        shuffled = random_degree_preserving(graph, 7)
        self.assertEqual(set(graph.edges()), edges)
        self.assertEqual(dict(shuffled.degree()), dict(graph.degree()))
        self.assertEqual(list(nx.selfloop_edges(shuffled)), [])

    def test_incomplete_randomization_reported(self):
        with self.assertWarns(RuntimeWarning):
            graph = random_degree_preserving(nx.complete_graph(4), 42)
        self.assertFalse(graph.graph['swap_target_reached'])

if __name__ == '__main__':
    unittest.main()

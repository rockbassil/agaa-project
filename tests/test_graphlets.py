import sys
import unittest
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

if __name__ == '__main__':
    unittest.main()

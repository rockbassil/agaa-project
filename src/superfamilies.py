"""Induced connected four-vertex graphlets and degree-preserving null models."""
import argparse
import csv
import json
import math
import random
from pathlib import Path

import networkx as nx

MOTIFS = ('P4', 'K1_3', 'C4', 'paw', 'diamond', 'K4')


def read_edge_list(path):
    graph = nx.Graph()
    with open(path, encoding='utf-8') as handle:
        for number, line in enumerate(handle, 1):
            line = line.split('#', 1)[0].strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 2:
                raise ValueError(f'{path}:{number}: expected two vertex identifiers')
            u, v = parts
            if u != v:
                graph.add_edge(u, v)
    return graph


def datasets():
    return {
        'karate': nx.karate_club_graph(),
        'florentine': nx.florentine_families_graph(),
        'southern_women': nx.davis_southern_women_graph(),
        'les_miserables': nx.les_miserables_graph(),
    }


def motif_type(graph, nodes):
    degrees = sorted(graph.degree(v) for v in nodes)
    edges = graph.number_of_edges()
    if edges == 3:
        return 'K1_3' if degrees == [1, 1, 1, 3] else 'P4'
    if edges == 4:
        return 'C4' if degrees == [2, 2, 2, 2] else 'paw'
    if edges == 5:
        return 'diamond'
    if edges == 6:
        return 'K4'
    raise ValueError('Expected a connected induced four-node graph')


def count_graphlets(graph):
    """Enumerate connected four-node vertex sets once, then classify induced edges."""
    graph = nx.Graph(graph)
    graph.remove_edges_from(nx.selfloop_edges(graph))
    adj = {v: set(graph.neighbors(v)) for v in graph}
    sets = set()
    # Grow connected sets: a connected four-set has a connected three-set
    # obtainable by adding one neighbor to a connected two-set.
    for u, v in graph.edges():
        two = frozenset((u, v))
        for w in (adj[u] | adj[v]) - two:
            three = two | {w}
            for x in (adj[u] | adj[v] | adj[w]) - three:
                sets.add(three | {x})
    counts = dict.fromkeys(MOTIFS, 0)
    for nodes in sets:
        verts = list(nodes)
        deg = {v: 0 for v in verts}
        edges = 0
        for i in range(4):
            for j in range(i + 1, 4):
                if verts[j] in adj[verts[i]]:
                    edges += 1
                    deg[verts[i]] += 1
                    deg[verts[j]] += 1
        signature = tuple(sorted(deg.values()))
        if edges == 3:
            name = 'K1_3' if signature == (1, 1, 1, 3) else 'P4'
        elif edges == 4:
            name = 'C4' if signature == (2, 2, 2, 2) else 'paw'
        elif edges == 5:
            name = 'diamond'
        else:
            name = 'K4'
        counts[name] += 1
    return counts


def random_degree_preserving(graph, seed, swap_multiplier=5):
    """Simple-graph configuration null via degree-preserving double-edge swaps.

    Connectedness is NOT enforced: this is a simple-graph degree-sequence
    preserving null, not an independent multigraph stub-pairing draw.
    """
    graph = nx.Graph(graph)
    swaps = swap_multiplier * graph.number_of_edges()
    if graph.number_of_edges() < 2 or swaps == 0:
        return graph
    try:
        nx.double_edge_swap(graph, nswap=swaps, max_tries=max(100, swaps * 100), seed=seed)
    except (nx.NetworkXAlgorithmError, nx.NetworkXError):
        # A saturated degree sequence may permit no further swaps.
        pass
    return graph


def analyze(graph, repetitions=20, seed=42, swap_multiplier=5, epsilon=4.0):
    if repetitions < 1:
        raise ValueError('repetitions must be >= 1')
    if epsilon <= 0:
        raise ValueError('epsilon must be positive')
    graph = nx.Graph(graph)
    graph.remove_edges_from(nx.selfloop_edges(graph))
    observed = count_graphlets(graph)
    rng = random.Random(seed)
    null_counts = []
    for _ in range(repetitions):
        random_graph = random_degree_preserving(graph, rng.randrange(2**32), swap_multiplier)
        null_counts.append(count_graphlets(random_graph))
    means = {key: sum(row[key] for row in null_counts) / repetitions for key in MOTIFS}
    delta = {key: (observed[key] - means[key]) / (observed[key] + means[key] + epsilon) for key in MOTIFS}
    length = math.sqrt(sum(value * value for value in delta.values()))
    srp = {key: (delta[key] / length if length else 0.0) for key in MOTIFS}
    return {
        'vertices': graph.number_of_nodes(), 'edges': graph.number_of_edges(),
        'repetitions': repetitions, 'seed': seed, 'swap_multiplier': swap_multiplier,
        'epsilon': epsilon, 'observed': observed, 'null_mean': means,
        'delta': delta, 'srp': srp,
    }


def save_results(results, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    with (output / 'profiles.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.writer(handle)
        writer.writerow(['dataset', 'nodes', 'edges', 'motif', 'observed', 'null_mean', 'delta', 'srp'])
        for name, result in results.items():
            for motif in MOTIFS:
                writer.writerow([name, result['vertices'], result['edges'], motif,
                                 result['observed'][motif], result['null_mean'][motif],
                                 result['delta'][motif], result['srp'][motif]])
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 5))
        for name, result in results.items():
            ax.plot(MOTIFS, [result['srp'][m] for m in MOTIFS], marker='o', label=name)
        ax.axhline(0, color='gray', linewidth=0.8)
        ax.set(xlabel='Connected induced four-node graphlet', ylabel='SRP', title='Subgraph ratio profiles')
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(output / 'profiles.png', dpi=160)
        plt.close(fig)
    except ImportError:
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', action='append', choices=tuple(datasets()) + ('all',), default=[])
    parser.add_argument('--edge-list', action='append', type=Path, default=[], help='Custom undirected edge list (u v per line)')
    parser.add_argument('--repetitions', type=int, default=20)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--swap-multiplier', type=int, default=5)
    parser.add_argument('--epsilon', type=float, default=4.0)
    parser.add_argument('--output', type=Path, default=Path('results'))
    args = parser.parse_args()
    chosen = datasets()
    selected = chosen if not args.dataset or 'all' in args.dataset else {k: chosen[k] for k in args.dataset}
    selected = dict(selected)
    for path in args.edge_list:
        selected[path.stem] = read_edge_list(path)
    results = {}
    for name, graph in selected.items():
        print(f'Analyzing {name}: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges...', flush=True)
        results[name] = analyze(graph, args.repetitions, args.seed, args.swap_multiplier, args.epsilon)
        print('  SRP:', {m: round(results[name]['srp'][m], 3) for m in MOTIFS}, flush=True)
    save_results(results, args.output)
    print(f'Results saved to {args.output}')


if __name__ == '__main__':
    main()

"""Rebuild the undirected food webs from the archived source files."""
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def write_edges(name, edges, expected_nodes):
    edges = sorted({tuple(sorted((u, v))) for u, v in edges if u != v})
    assert {v for edge in edges for v in edge} == set(expected_nodes)
    (ROOT / name).write_text(
        '# Undirected, unweighted; see data/README.md for preprocessing.\n'
        + ''.join(f'{u} {v}\n' for u, v in edges), encoding='utf-8')


def main():
    sources = {
        'st_marks_original.txt': '786f45bf56dbb90d3d8b62d0da6c52c0',
        'benguela_original.py.txt': '0c8ab6647303f0b35c3f7d57ae8a7e75',
    }
    for name, expected in sources.items():
        assert hashlib.md5((ROOT / name).read_bytes()).hexdigest() == expected, name
    edges = []
    for line in (ROOT / 'st_marks_original.txt').read_text().splitlines():
        if line.startswith('#') or not line.strip():
            continue
        u, v = map(int, line.split())
        if 0 not in (u, v):
            edges.append((u, v))
    write_edges('st_marks.txt', edges, range(1, 49))
    # Parse only the empirical 29 x 29 matrix. Never execute downloaded code.
    text = (ROOT / 'benguela_original.py.txt').read_text().split('# Add root')[0]
    edges = [(int(u), int(v)) for u, v in re.findall(r'B7\[(\d+)\]\[(\d+)\] = 1', text)]
    write_edges('benguela.txt', edges, range(29))


if __name__ == '__main__':
    main()

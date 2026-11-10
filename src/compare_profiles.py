"""Compare SRPs and record sensitivity to the seed and swap budget."""
import csv
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from superfamilies import MOTIFS

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT / 'results'
    base = json.loads((folder / 'results.json').read_text())
    names = list(base)
    vectors = np.array([[base[name]['srp'][m] for m in MOTIFS] for name in names])
    # Cosine measures direction in the original SRP coordinates, without centering.
    cosine = vectors @ vectors.T
    with (folder / 'similarities.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.writer(handle, lineterminator='\n')
        writer.writerow(['dataset'] + names)
        for name, row in zip(names, cosine):
            writer.writerow([name] + list(row))
    fig, ax = plt.subplots(figsize=(7.5, 6))
    plot = ax.imshow(cosine, cmap='RdBu_r', vmin=-1, vmax=1)
    ax.set_xticks(range(len(names)), names, rotation=35, ha='right')
    ax.set_yticks(range(len(names)), names)
    for i in range(len(names)):
        for j in range(len(names)):
            ax.text(j, i, f'{cosine[i,j]:.2f}', ha='center', va='center',
                    color='white' if abs(cosine[i,j]) > .7 else 'black')
    fig.colorbar(plot, ax=ax, label='Cosine des profils SRP')
    fig.tight_layout()
    fig.savefig(folder / 'similarities.png', dpi=180)
    plt.close(fig)
    sensitivity = {}
    for alternative in ('seed43', 'swaps20'):
        other = json.loads((folder / alternative / 'results.json').read_text())
        sensitivity[alternative] = {}
        for name in names:
            a = base[name]['srp']
            b = other[name]['srp']
            sensitivity[alternative][name] = {
                'cosine': sum(a[m] * b[m] for m in MOTIFS),
                'l2_distance': math.sqrt(sum((a[m] - b[m])**2 for m in MOTIFS)),
                'max_absolute_difference': max(abs(a[m] - b[m]) for m in MOTIFS),
            }
    (folder / 'sensitivity.json').write_text(json.dumps(sensitivity, indent=2), encoding='utf-8')
    print(json.dumps(sensitivity, indent=2))


if __name__ == '__main__':
    main()

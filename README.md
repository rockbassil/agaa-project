# AAGA — Sujet 7 : Superfamilles de réseaux complexes

Comparaison de réseaux non orientés par les six graphlets connexes induits à
quatre sommets et les profils SRP de Milo et al. (2004).

## Livrables

- `rapport.pdf` : rapport français de **10 pages**, références comprises.
- `rapport.md` : export éditable du texte et des tableaux.
- `VERIFICATION.md` : contrôle des exigences et réserves.
- `src/superfamilies.py` : comptage, randomisation, SRP et export.
- `src/compare_profiles.py` : comparaison et sensibilité.
- `tests/test_graphlets.py` : dix tests, dont le contrôle des 1 253 graphes du catalogue NetworkX.
- `data/` : réseaux écologiques archivés et prétraitement documenté.
- `results/` : expérience principale et deux contrôles.
- `run_experiments.sh` : commandes de reproduction des expériences.

## Installation et reproduction

Python 3.10 ou supérieur. Les versions exactes utilisées figurent dans les JSON.
La graine seule ne garantit pas l'identité entre versions de bibliothèques.

```bash
python -m pip install -r requirements.txt
bash run_experiments.sh
```

Le script prépare les données, lance les tests, puis trois expériences sur les
six réseaux : 100 tirages, graine 42, 5 échanges par arête ; 100 tirages, graine
43, 5 échanges ; 100 tirages, graine 42, 20 échanges. Les données sont archivées :
aucun téléchargement n'est nécessaire pour les simulations. Prévoir plusieurs
minutes selon la machine. Aucun Makefile n'est nécessaire pour Python.

Commandes équivalentes sous PowerShell :

```powershell
python data/prepare_data.py
python -m unittest discover -s tests -v
python src/superfamilies.py --dataset all --repetitions 100 --seed 42 --swap-multiplier 5 --output results
python src/superfamilies.py --dataset all --repetitions 100 --seed 43 --swap-multiplier 5 --output results/seed43
python src/superfamilies.py --dataset all --repetitions 100 --seed 42 --swap-multiplier 20 --output results/swaps20
python src/compare_profiles.py
```

Ces commandes Python ont été exécutées sous Windows. Le lancement Bash sur les
machines de la PPTI reste à vérifier.

## Options des commandes

```bash
python src/superfamilies.py --help
```

| Option | Rôle et valeur par défaut |
|---|---|
| `--dataset NAME` | `karate`, `florentine`, `southern_women`, `les_miserables`, `st_marks`, `benguela`, ou `all`. Répétable. Sans sélection ni fichier externe : tous les réseaux. |
| `--edge-list PATH` | Graphe au format `u v`, une arête par ligne. Répétable. Utilisée seule : seuls les fichiers indiqués sont analysés. |
| `--repetitions N` | Nombre de graphes aléatoires, au moins 1. Défaut : 20 ; expériences livrées : 100. |
| `--seed N` | Graine initiale. Défaut : 42. |
| `--swap-multiplier N` | Entier positif ou nul : échanges réussis demandés par arête. Défaut : 5. Zéro désactive la randomisation. |
| `--epsilon X` | Régularisation strictement positive. Défaut : 4. |
| `--output DIR` | Dossier de sortie. Défaut : `results`. |

Les commentaires commencent par `#`. Doublons et liens réciproques sont
fusionnés ; les boucles sont retirées mais leurs sommets sont conservés.
Le format ne décrit pas séparément les sommets isolés : les ajouter dans le code
si nécessaire. Les noms des jeux de données doivent être distincts.

## Méthode et limites

Chaque ensemble connexe de quatre sommets est compté une seule fois. Le graphe
induit comprend toutes les arêtes entre ces sommets. Ordre des motifs :
`P4`, `K1_3`, `C4`, `paw`, `diamond`, `K4`.

```text
delta_i = (N_i - R_i) / (N_i + R_i + epsilon)
SRP_i = delta_i / sqrt(sum_j delta_j**2)
```

`N_i` est le comptage observé, `R_i` la moyenne aléatoire. Si tous les écarts
sont nuls, le profil est nul. Le modèle conserve exactement les degrés dans
des graphes simples par échanges doubles d'arêtes. Il approche l'ensemble de
configuration conditionné à rester simple, sans garantie de mélange uniforme
après un nombre fini d'échanges. Il ne conserve ni connexité ni bipartition.
Un échec de randomisation est signalé et enregistré dans le JSON.

Les quatre jeux NetworkX décrivent un club, des mariages, des affiliations et
des coapparitions de personnages. Les réseaux trophiques St. Marks et Benguela
ajoutent un domaine écologique. Leur origine et leurs transformations sont
documentées dans [data/README.md](data/README.md). Orientation et poids sont ignorés.
Southern women reste biparti, sans projection ; son contraste avec une référence
non bipartie doit être interprété en conséquence. Le réseau littéraire provient
d'une œuvre, et non d'observations de personnes réelles. Six réseaux permettent
une comparaison exploratoire, sans établir une classification générale.

## Sorties et rapport

`results.json` conserve les paramètres, versions, comptages observés et aléatoires,
moyennes, écarts-types, écarts relatifs, SRP et diagnostics. `profiles.csv` et
`profiles.png` présentent les profils. `similarities.csv` et `similarities.png`
comparent les profils par cosinus ; `sensitivity.json` mesure leur variation.
Les contrôles se trouvent dans `seed43/` et `swaps20/`.

```bash
python -m pip install -r requirements-report.txt
python src/build_report.py
```

Le script utilise les résultats existants, produit le PDF et vérifie ses dix
pages. Il écrit aussi `rapport.md`. Le texte utilisé pour régénérer le PDF est
dans `src/build_report.py` : modifier seulement l'export Markdown ne modifie pas
le PDF. Arial est utilisée sous Windows, DejaVu Sans sous Linux. Une variation
de pagination liée aux polices est signalée par le contrôle du nombre de pages.

## Références

Milo et al. (2004), *Superfamilies of Evolved and Designed Networks*, Science
303(5663), 1538–1542. PDF fourni dans le dossier.

Calò (2025), *Food webs: edge lists and species names*, Zenodo,
https://doi.org/10.5281/zenodo.15045517.

NetworkX : https://networkx.org/documentation/stable/reference/generators/social.html.

# Réseaux trophiques

Source : Emanuele Calò (2025), *Food webs: edge lists and species names*, version 1,
Zenodo, https://doi.org/10.5281/zenodo.15045517 (consulté le 10 novembre 2026).
Les fichiers originaux et les listes de groupes biologiques sont conservés ici.
Les empreintes MD5 publiées sont contrôlées par `prepare_data.py`.

Références empiriques indiquées par le dépôt :

- St. Marks : R. R. Christian et J. J. Luczkovich (1999), *Organizing and understanding a winter’s seagrass foodweb network through effective trophic levels*, Ecological Modelling 117, 99.
- Benguela : P. Yodzis (1998), *Local trophodynamics and the interaction of marine mammals and fisheries in the Benguela ecosystem*, Journal of Animal Ecology 67, 635.

## Prétraitement reproductible

Exécuter `python data/prepare_data.py`. Aucun code téléchargé n'est exécuté.

Pour St. Marks, le fichier contient les identifiants 0 à 48, alors que son en-tête
et la liste biologique indiquent 48 groupes. On écarte le sommet supplémentaire
0 et ses six liens, puis on conserve les sommets 1 à 48. Ce choix traite 0 comme
un ajout extérieur à la liste biologique ; son rôle de racine est une interprétation
de la structure du fichier, et non une annotation explicite de celui-ci.

Pour Benguela, on extrait uniquement les affectations de la matrice initiale
29 × 29, avant le commentaire explicite `# Add root`. Les insertions ultérieures
de racine et les corrections indexées après insertion ne sont pas appliquées.
Après retrait de la racine, ces dernières n'ajoutent pas de nouvelle paire de
sommets distincts à la version non orientée : les paires existent déjà en sens inverse.

Dans les deux cas, on oublie l'orientation, on retire les boucles et on fusionne
les interactions réciproques. Tous les sommets biologiques restent présents.
Le résultat représente l'existence d'une interaction trophique, sans son sens,
sa force ni sa fréquence. Ces choix doivent accompagner toute interprétation.

Les données sont nouvelles pour cette expérience par rapport aux réseaux
énumérés dans le corps et les figures de l'article de Milo et al. fourni.
La table S1 du supplément n'est pas fournie ; son contenu n'a pas été vérifié.

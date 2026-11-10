# Vérification du projet

Contrôle effectué le 10 novembre 2026 à partir de `projet_superfamilies.pdf`,
de l'article de Milo et al. fourni et des fichiers du projet.

## Bilan des exigences

| Exigence | État | Éléments et limites |
|---|---|---|
| Rapport d'environ 10 pages | Satisfait | `rapport.pdf` contient exactement 10 pages, bibliographie incluse. |
| Implémentation | Satisfait | Python ; pas de compilation ni de Makefile nécessaires. |
| Fichier Bash lançant les simulations | Fourni | `run_experiments.sh` contient les trois expériences. Les commandes Python ont été exécutées sous Windows ; le lancement Bash sur la PPTI reste à vérifier. |
| Documentation des commandes | Satisfait | README et `--help`, formats d'entrée et paramètres décrits. |
| Comptage non orienté à quatre sommets au minimum | Satisfait | Les six graphlets connexes induits sont comptés exactement. |
| Modèle de configuration et SRP | Satisfait avec convention explicitée | Ensemble simple à degrés fixés approché par échanges doubles. Formule SRP et epsilon = 4 conformes à la partie non orientée de l'article, p. 1541. Ni appariement indépendant de demi-arêtes ni garantie de mélange uniforme à temps fini. |
| Plusieurs types de graphes réels, nouveaux par rapport à l'article | Couvert avec réserve documentaire | Réseaux sociaux, affiliation et deux réseaux trophiques ; réseau littéraire complémentaire. Ces jeux ne sont pas nommés dans le corps ou les figures du PDF. Sa table supplémentaire S1 n'est pas jointe et n'a pas été contrôlée. |
| Examiner les superfamilles | Réalisé, portée exploratoire | Profils, cosinus et sensibilité calculés. Le corpus ne démontre pas une classification générale. |

Les livrables et le contenu demandés sont présents. Une validation sans réserve
nécessite encore de vérifier le lancement sur la PPTI et, si l'exclusion exacte
de tous les jeux originaux est exigée, la table S1 du supplément de l'article.
L'appréciation pédagogique de la convention retenue pour le modèle de
configuration appartient à l'enseignant.

## Vérifications réalisées

- Dix tests passent, dont un contrôle indépendant des 1 253 graphes simples non étiquetés d'au plus sept sommets du catalogue NetworkX.
- Conservation exacte des degrés, du graphe d'entrée et de la simplicité ; formule SRP et répétabilité vérifiées.
- Trois expériences sur six réseaux avec 100 graphes aléatoires chacun : 1 800 graphes de référence au total.
- Graine 42 / cinq échanges par arête ; graine 43 / cinq échanges ; graine 42 / vingt échanges.
- Paramètres, versions, comptages individuels et diagnostics archivés dans les JSON.
- Empreintes MD5 des fichiers écologiques comparées à celles du dépôt Zenodo.
- Nombre de pages contrôlé par lecture du PDF.
- Mise en page des dix pages contrôlée visuellement ; syntaxe Bash vérifiée avec `bash -n`.

## Corrections et révision du texte

Le README annonçait un rapport absent et décrivait seulement quatre réseaux,
principalement sociaux ou littéraires. Le rapport a été rédigé à partir des
résultats recalculés. Les formulations vagues et répétitives ont été remplacées
par une documentation précise en français. Les références et les limites
scientifiques ont été conservées.

Le programme signale les échanges incomplets, conserve les comptages aléatoires
et les versions, accepte les réseaux écologiques et évite d'analyser tous les
jeux intégrés lorsqu'un seul fichier externe est demandé. Le contrôle des noms
empêche l'écrasement silencieux d'un jeu par un autre.

## Réserves scientifiques

Le modèle ne conserve ni bipartition ni connexité. Les réseaux trophiques sont
symétrisés et leurs boucles retirées. Le sommet 0 de St. Marks est exclu car il
est absent de la liste des 48 groupes biologiques ; son interprétation comme
racine ajoutée reste une inférence. Deux graines et l'augmentation des échanges
fournissent des contrôles pratiques, sans démontrer la convergence. Le SRP n'est
pas une valeur p. Le corpus reste limité pour conclure sur les superfamilles.

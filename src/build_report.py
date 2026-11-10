"""Build the ten-page French report and its editable Markdown counterpart."""
import json
import math
import os
from pathlib import Path
import sys
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.report_deps'))
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from pypdf import PdfReader

from superfamilies import MOTIFS


def main():
    results = json.loads((ROOT / 'results/results.json').read_text())
    sensitivity = json.loads((ROOT / 'results/sensitivity.json').read_text())
    names = list(results)
    fonts = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
    if (fonts / 'arial.ttf').exists():
        pdfmetrics.registerFont(TTFont('Body', str(fonts / 'arial.ttf')))
        pdfmetrics.registerFont(TTFont('BodyBold', str(fonts / 'arialbd.ttf')))
    else:
        # DejaVu is commonly installed on Linux teaching workstations.
        fonts = Path('/usr/share/fonts/truetype/dejavu')
        pdfmetrics.registerFont(TTFont('Body', str(fonts / 'DejaVuSans.ttf')))
        pdfmetrics.registerFont(TTFont('BodyBold', str(fonts / 'DejaVuSans-Bold.ttf')))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BodyTextReport', fontName='Body', fontSize=10.3,
                              leading=15.2, spaceAfter=9, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='TitleReport', fontName='BodyBold', fontSize=21,
                              leading=26, textColor=colors.HexColor('#173d56'), spaceAfter=18))
    styles.add(ParagraphStyle(name='SubReport', fontName='BodyBold', fontSize=11.5,
                              leading=16, spaceBefore=10, spaceAfter=8))
    styles.add(ParagraphStyle(name='CellReport', fontName='Body', fontSize=8.1, leading=11))
    styles.add(ParagraphStyle(name='CaptionReport', fontName='Body', fontSize=8.7,
                              leading=12, spaceAfter=11, textColor=colors.HexColor('#455363')))
    story, markdown = [], []

    def page(title):
        if story:
            story.append(PageBreak())
            markdown.append('\n---\n')
        story.append(Paragraph(escape(title), styles['TitleReport']))
        markdown.append('# ' + title + '\n')

    def p(text):
        story.append(Paragraph(escape(text), styles['BodyTextReport']))
        markdown.append(text + '\n')

    def h(text):
        story.append(Paragraph(escape(text), styles['SubReport']))
        markdown.append('## ' + text + '\n')

    def table(headers, rows, widths=None):
        content = [[Paragraph(escape(str(cell)), styles['CellReport']) for cell in row]
                   for row in [headers] + rows]
        tab = Table(content, colWidths=widths, repeatRows=1, hAlign='LEFT')
        tab.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dfebf1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f4f6f8')]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('LINEBELOW', (0, 0), (-1, 0), .6, colors.HexColor('#92a9b8')),
        ]))
        story.extend([tab, Spacer(1, 12)])
        markdown.append('| ' + ' | '.join(headers) + ' |')
        markdown.append('|' + '|'.join(['---'] * len(headers)) + '|')
        markdown.extend('| ' + ' | '.join(map(str, row)) + ' |' for row in rows)
        markdown.append('')

    def fig(path, width, height, caption):
        story.append(Image(str(ROOT / path), width=width, height=height))
        story.append(Paragraph(escape(caption), styles['CaptionReport']))
        markdown.append(f'![{caption}]({path})\n')

    def cosine(a, b):
        return sum(results[a]['srp'][m] * results[b]['srp'][m] for m in MOTIFS)

    page('Superfamilles de réseaux complexes')
    p('Projet AAGA — Sujet 7 | Étude de graphes non orientés | 10 novembre 2026')
    h('Résumé')
    p('Deux réseaux peuvent avoir des tailles et des degrés très différents tout en présentant des organisations locales proches. Le projet étudie cette idée à partir des six graphlets connexes à quatre sommets. Leur fréquence observée est comparée à celle de graphes aléatoires conservant les degrés, puis résumée par un profil SRP. La démarche reprend la partie non orientée de l’article de Milo et al. [1], en l’appliquant à un autre corpus.')
    p('Le programme dénombre exactement les occurrences induites. Les expériences portent sur six réseaux : deux réseaux de relations sociales, un réseau d’affiliation, un réseau de personnages et deux réseaux trophiques. Pour chacun, cent graphes aléatoires servent à estimer les fréquences de référence. Deux expériences supplémentaires modifient séparément la graine et le nombre d’échanges d’arêtes. Les résultats numériques, les figures et les commandes nécessaires à leur reproduction accompagnent le rapport.')
    p('L’objectif est de distinguer une ressemblance mesurée d’une conclusion sur une famille de réseaux. Un profil commun fournit une piste de comparaison ; il ne suffit pas à établir une origine commune ou une même fonction. Cette prudence est particulièrement nécessaire lorsque les données sont petites, biparties ou obtenues en supprimant l’orientation des interactions.')
    h('Question étudiée')
    p('La conservation de la séquence des degrés suffit-elle à expliquer les motifs observés ? Si ce n’est pas le cas, les écarts se ressemblent-ils entre réseaux de même nature, ou entre domaines différents ? Ces deux questions organisent l’analyse. La première concerne chaque réseau ; la seconde porte sur la comparaison des profils normalisés.')
    table(['Parcours du rapport', 'Page'], [
        ['Article de référence et définition des motifs', '2'],
        ['Algorithme de comptage et modèle aléatoire', '3–4'],
        ['Données et résultats expérimentaux', '5–6'],
        ['Comparaison et sensibilité des profils', '7–8'],
        ['Validation, conclusion et références', '9–10']], [395, 80])

    page('1. De l’article aux motifs étudiés')
    p('Milo et al. [1] comparent des réseaux à travers leur structure locale. Leur étude distingue les graphes orientés, décrits notamment par des triades, et les graphes non orientés, pour lesquels ils examinent six tétrades connexes. Le présent projet se limite à ce second cadre, comme le demande le sujet [2]. Les conclusions concernant les réseaux orientés ne sont donc pas transposées directement aux expériences réalisées ici.')
    p('Un graphlet induit sur un ensemble de quatre sommets contient toutes les arêtes du graphe initial entre ces sommets. Cette convention compte une occurrence par ensemble de sommets, sans distinguer ses automorphismes. Elle empêche de compter une clique de quatre sommets comme plusieurs chemins ou cycles : ses six arêtes déterminent le type K4. Les ensembles non connexes ne sont pas retenus.')
    table(['Motif', 'Arêtes', 'Degrés internes triés', 'Description'], [
        ['P4', '3', '1, 1, 2, 2', 'Chemin de longueur 3'],
        ['K1,3', '3', '1, 1, 1, 3', 'Étoile à trois branches'],
        ['C4', '4', '2, 2, 2, 2', 'Cycle sans diagonale'],
        ['paw', '4', '1, 2, 2, 3', 'Triangle avec sommet pendant'],
        ['diamond', '5', '2, 2, 3, 3', 'Clique privée d’une arête'],
        ['K4', '6', '3, 3, 3, 3', 'Clique complète']], [55, 45, 150, 225])
    p('Le nombre d’arêtes et les degrés internes suffisent à distinguer ces six graphes. Ce raccourci est valable dans ce catalogue restreint ; il ne constitue pas un test général d’isomorphisme. Pour des motifs plus grands, plusieurs graphes non isomorphes peuvent partager la même séquence de degrés.')
    h('Pourquoi ne pas comparer les nombres bruts ?')
    p('Un réseau plus grand offre davantage de quadruplets possibles. Des sommets de degré élevé produisent aussi beaucoup d’étoiles et de chemins, même sans organisation particulière. Le modèle aléatoire sert à comparer le graphe à une référence qui partage sa séquence des degrés. Le SRP décrit ainsi un écart relatif à cette référence, et non une propriété indépendante de tout modèle.')
    p('Dans la partie non orientée de l’article, les auteurs utilisent un rapport régularisé plutôt que les scores Z normalisés employés pour les triades orientées. Le programme reprend ce choix avec epsilon égal à 4. L’ordre des motifs utilisé dans les fichiers est explicite : P4, K1_3, C4, paw, diamond, K4. Les noms priment sur la numérotation des schémas de l’article.')

    page('2. Un dénombrement exact')
    p('La fonction count_graphlets commence par construire un graphe simple non orienté et par retirer les boucles. Elle prépare ensuite l’ensemble des voisins de chaque sommet. Les poids éventuellement présents dans les jeux de données ne jouent aucun rôle dans ce comptage topologique.')
    h('Construction des ensembles connexes')
    p('L’énumération part de chaque arête {u, v}. Elle lui ajoute un voisin de u ou de v pour obtenir trois sommets connexes. Un quatrième sommet est choisi parmi les voisins de ces trois sommets. Les ensembles produits sont enregistrés sous forme d’ensembles immuables dans une table de hachage. Un même quadruplet peut être construit de plusieurs façons, mais n’est conservé qu’une fois.')
    p('Tout ensemble ainsi construit est connexe, puisque chaque sommet ajouté est relié à l’ensemble précédent. Réciproquement, un graphe connexe à quatre sommets possède un arbre couvrant. En retirant une feuille de cet arbre, on obtient trois sommets connexes ; en retirant une autre feuille, on obtient une arête. La procédure peut donc reconstruire tout quadruplet connexe. Elle est exhaustive et ne se limite pas à un échantillon.')
    h('Classification des occurrences')
    p('Pour chaque ensemble distinct, les six paires de sommets sont examinées. Le programme compte les arêtes présentes et les degrés internes, puis applique le tableau de la page précédente. Les arêtes sont lues dans le graphe initial : les éventuelles diagonales font donc partie du sous-graphe. C’est cette étape qui assure le caractère induit du comptage.')
    h('Coût et domaine d’utilisation')
    p('Si Q désigne le nombre de quadruplets connexes distincts, leur classification demande O(Q) opérations à un facteur constant près. La construction peut revisiter un même ensemble de nombreuses fois. Une borne grossière du travail de génération est O(m × D²), où m est le nombre d’arêtes et D le degré maximal. Le stockage des ensembles demande O(Q), en plus des listes de voisinage. Dans un graphe dense, Q peut atteindre le nombre total de quadruplets, soit une croissance en n à la puissance quatre.')
    p('Cette méthode convient aux réseaux de quelques dizaines de sommets retenus ici. Elle devient coûteuse pour de grands réseaux ou en présence de très grands degrés. Une extension à cette échelle demanderait un algorithme d’énumération évitant les doublons dès la construction, une méthode combinatoire spécialisée, ou un échantillonnage avec estimation de son erreur.')
    p('La correction du dénombrement est contrôlée indépendamment par une énumération exhaustive des quadruplets et un test d’isomorphisme. Ce contrôle porte sur les 1 253 graphes simples non étiquetés d’au plus sept sommets du catalogue de NetworkX. Il vérifie notamment les graphes contenant plusieurs composantes, des triangles et des motifs qui se recouvrent.')

    page('3. Modèle aléatoire et calcul du SRP')
    p('Le modèle de configuration fixe les degrés des sommets. Sa construction classique apparie aléatoirement des demi-arêtes et peut créer des boucles ou des arêtes multiples. Pour rester dans le même espace que les données, l’implémentation travaille dans l’ensemble des graphes simples possédant la séquence de degrés observée. Elle approche cet ensemble par échanges doubles d’arêtes, plutôt que par un appariement direct de demi-arêtes suivi d’une simplification qui modifierait les degrés.')
    p('Un échange remplace deux arêtes par deux autres, en préservant le degré de chaque sommet. NetworkX refuse les propositions qui créent des arêtes multiples. Les sommets, le nombre d’arêtes et tous les degrés sont conservés ; la connexité et la bipartition ne sont pas imposées. Chaque tirage repart du graphe observé avec une graine issue du générateur initialisé par la graine de l’expérience.')
    h('Estimation de la référence')
    p('Pour le motif i, N_i désigne le nombre observé. Avec B = 100 graphes aléatoires, R_i est la moyenne de leurs B comptages. Le programme conserve aussi ces comptages individuels et leur écart-type empirique. Ce dernier décrit la dispersion dans l’ensemble simulé ; il n’entre pas dans la formule du SRP.')
    table(['Quantité', 'Définition'], [
        ['Moyenne aléatoire', 'R_i = (1/B) × somme des N_i des graphes aléatoires'],
        ['Écart relatif régularisé', 'delta_i = (N_i − R_i) / (N_i + R_i + 4)'],
        ['Normalisation', 'L = racine de la somme des delta_i²'],
        ['Profil', 'SRP_i = delta_i / L si L > 0 ; 0 sinon']], [145, 330])
    p('Le terme 4 limite l’importance d’un écart portant sur quelques occurrences seulement. Le signe du SRP indique une surreprésentation ou une sous-représentation par rapport au modèle. La normalisation donne une norme égale à 1 lorsque le vecteur des écarts est non nul. Elle conserve la direction des écarts, mais efface leur amplitude globale. Deux profils proches peuvent donc correspondre à des écarts absolus très différents.')
    h('Précautions sur les tirages')
    p('L’expérience principale demande 5m échanges réussis par graphe aléatoire. Le nombre maximal de tentatives vaut 100 fois cette cible, avec un minimum de 100. Un échec est signalé et enregistré. Des graines distinctes ne garantissent ni un mélange suffisant ni un échantillonnage uniforme à temps fini. Le passage à 20m échanges constitue un contrôle pratique de sensibilité, sans démontrer la convergence vers la distribution stationnaire.')

    page('4. Corpus et préparation des données')
    table(['Réseau', 'n', 'm', 'Nature de la relation'], [
        [name, results[name]['vertices'], results[name]['edges'], desc]
        for name, desc in zip(names, ['Relations au sein d’un club', 'Mariages entre familles',
                                    'Participation à des événements', 'Coapparition de personnages',
                                    'Interactions trophiques', 'Interactions trophiques'])], [110, 30, 35, 300])
    p('Les quatre premiers réseaux sont distribués avec NetworkX [3]. Karate décrit des relations dans le club étudié par Zachary. Florentine représente des mariages entre familles florentines. Southern women relie des femmes à des événements auxquels elles ont participé. Les Misérables relie des personnages qui apparaissent ensemble. Ce dernier est un réseau construit à partir d’une œuvre ; il ne décrit pas des interactions observées entre personnes réelles.')
    p('Les réseaux trophiques St. Marks et Benguela proviennent du dépôt de Calò [4]. Ils apportent un domaine écologique au corpus. Les fichiers originaux, leurs listes biologiques et les empreintes de contrôle sont conservés dans data/. Leur transformation est effectuée par un script local, sans exécuter le fichier Python téléchargé.')
    h('Choix de préparation')
    p('St. Marks contient un identifiant supplémentaire 0 par rapport aux 48 groupes biologiques annoncés. Ce sommet et ses six liens sont écartés. Benguela est extrait de la matrice initiale de 29 groupes, avant l’ajout explicite d’une racine. Dans les deux réseaux, l’orientation est supprimée, les boucles sont retirées et les liens réciproques sont fusionnés. Les détails et les réserves sur ces choix figurent dans data/README.md.')
    p('L’analyse écologique porte donc sur l’existence d’une interaction, et non sur le sens du transfert trophique. Cette perte d’information est assumée pour respecter le cadre non orienté du sujet. Les espèces ou groupes biologiques ne sont pas assimilés à des protéines : la proximité éventuelle avec d’autres profils doit être interprétée à l’échelle de la structure retenue.')
    h('Portée du corpus')
    p('Les jeux retenus ne sont pas ceux nommés dans le corps et les figures du PDF de référence. Le supplément contenant la table S1 n’est pas joint ; son inventaire complet n’a pas été contrôlé. Le corpus reste modeste : seuls les réseaux trophiques fournissent deux exemples d’un même domaine biologique. Il permet une comparaison exploratoire, mais ne représente pas l’ensemble des réseaux sociaux, écologiques ou techniques.')
    p('Southern women est conservé comme graphe biparti, sans projection. Il ne contient donc aucun triangle. Le modèle aléatoire préserve les degrés mais autorise des liens au sein d’un même groupe : une partie de l’écart mesuré reflète nécessairement cette différence de contraintes.')

    page('5. Résultats des expériences')
    p('Les tableaux ci-dessous utilisent l’expérience principale : B = 100, graine 42, cinq échanges réussis par arête et epsilon = 4. Les valeurs de SRP sont arrondies à trois décimales pour la lecture. Les fichiers JSON et CSV conservent la précision numérique et les moyennes de référence pour chaque motif.')
    table(['Réseau'] + list(MOTIFS), [[name] + [f"{results[name]['srp'][m]:.3f}" for m in MOTIFS]
                                               for name in names], [100] + [62.5] * 6)
    h('Comptages observés')
    table(['Réseau'] + list(MOTIFS), [[name] + [str(results[name]['observed'][m]) for m in MOTIFS]
                                               for name in names], [100] + [62.5] * 6)
    p('Les nombres bruts et les profils répondent à des questions différentes. Un motif fréquent peut présenter un SRP négatif si sa moyenne de référence est encore plus élevée. Inversement, quelques cliques peuvent produire un écart positif dans un petit graphe. L’examen simultané des comptages, des moyennes aléatoires et des rapports évite de confondre fréquence et surreprésentation.')
    p('Dans Les Misérables, le contraste entre les cycles sans diagonale et les cliques complètes est net. Les coapparitions dans un même groupe peuvent produire des zones très denses : cette interprétation est compatible avec le profil, sans être une explication causale démontrée. Le réseau Florentine est beaucoup plus petit. Plusieurs motifs y sont rares ; les composantes secondaires de son profil doivent donc être lues avec prudence.')
    p('Southern women donne un exemple particulièrement clair de l’effet du cadre de comparaison. Les motifs paw, diamond et K4 contiennent un triangle et sont absents du graphe observé. Leurs valeurs négatives ne prouvent pas une préférence sociale contre ces motifs : elles traduisent d’abord une propriété imposée par la bipartition que le modèle de référence ne conserve pas.')

    page('6. Comparer les profils')
    fig('results/profiles.png', 475, 237.5,
        'Figure 1 — Profils SRP obtenus avec 100 graphes aléatoires par réseau. Les lignes relient les catégories de motifs ; elles ne représentent pas une variable continue.')
    p('Pour comparer les directions des profils sans modifier leurs coordonnées, on utilise le cosinus. Comme chaque profil non nul a une norme égale à 1, ce cosinus est simplement le produit scalaire des six composantes. Une valeur proche de 1 indique des directions proches ; une valeur négative traduit des orientations opposées. Cette mesure diffère de la corrélation de Pearson utilisée pour certaines comparaisons dans l’article, qui centre les coordonnées avant de les comparer.')
    pairs = sorted(((cosine(a, b), a, b) for i, a in enumerate(names) for b in names[i + 1:]), reverse=True)
    table(['Paire de réseaux', 'Cosinus'], [[f'{a} / {b}', f'{value:.3f}'] for value, a, b in pairs[:4]], [370, 105])
    p(f"Pour les deux réseaux trophiques, le cosinus vaut {cosine('st_marks', 'benguela'):.3f}. Cette valeur décrit les versions non orientées et prétraitées, ainsi que le modèle de référence choisi. Elle ne mesure pas directement une similarité des mécanismes trophiques.")
    p('Le rapprochement le plus marqué concerne Karate et Les Misérables (cosinus 0,783). Les deux réseaux trophiques sont moins proches (0,561) : une même catégorie de données ne produit donc pas automatiquement un même profil. Aucun seuil statistique ne permet ici de transformer ces valeurs en appartenance à une famille.')
    p('Le petit nombre de réseaux rend fragile toute classification automatique. Un regroupement obtenu sur ces seuls six profils pourrait surtout refléter la présence de triangles, la bipartition ou la densité locale. Les rapprochements observés constituent donc des candidats à vérifier sur d’autres données, plutôt qu’une partition établie en superfamilles.')

    page('7. Stabilité et limites de l’expérience')
    p('Deux contrôles sont conduits avec le même nombre de tirages que l’expérience principale. Le premier remplace la graine 42 par 43 sans changer le nombre d’échanges. Le second conserve la graine 42 et porte la cible de 5m à 20m échanges. Chaque comparaison ne fait ainsi varier qu’un paramètre du protocole.')
    table(['Réseau', 'Cosinus : graine 43', 'Cosinus : 20m', 'Écart max. : 20m'], [
        [name, f"{sensitivity['seed43'][name]['cosine']:.3f}",
         f"{sensitivity['swaps20'][name]['cosine']:.3f}",
         f"{sensitivity['swaps20'][name]['max_absolute_difference']:.3f}"] for name in names],
        [115, 125, 110, 125])
    p('Le cosinus évalue la direction globale. L’écart maximal est la plus grande différence absolue entre deux composantes du SRP. Les distances euclidiennes sont aussi enregistrées dans sensitivity.json. Des profils proches selon le cosinus peuvent conserver des variations appréciables sur un motif rare ; il faut donc éviter de réduire le contrôle à un seul nombre.')
    worst = min(names, key=lambda name: sensitivity['seed43'][name]['cosine'])
    p(f"Le changement de graine affecte le plus la direction du profil de {worst}, avec un cosinus de {sensitivity['seed43'][worst]['cosine']:.3f}. Cette comparaison empirique donne une indication de stabilité sur deux réalisations ; elle ne fournit pas un intervalle de confiance.")
    incomplete = sum(r['incomplete_randomizations'] for r in results.values())
    p(f"Dans l’expérience principale, {incomplete} tirage(s) n’ont pas atteint la cible d’échanges. Le diagnostic est enregistré pour chaque réseau. Atteindre la cible confirme l’exécution des échanges demandés, mais ne prouve pas que l’état final est représentatif de tous les graphes simples ayant ces degrés.")
    h('Ce que ces contrôles ne résolvent pas')
    p('Cent tirages améliorent l’estimation par rapport aux vingt tirages initiaux du projet, sans garantir une précision suffisante pour tous les motifs. Aucun diagnostic de mélange fondé sur plusieurs longues chaînes n’est calculé. Les écarts-types des comptages aléatoires décrivent l’ensemble simulé ; ils ne quantifient pas les erreurs de mesure présentes dans les données réelles.')
    p('Le corpus contient des réseaux de tailles modestes et de constructions hétérogènes. Il manque notamment un domaine d’infrastructure et davantage de réseaux par catégorie. Pour vérifier la généralité des superfamilles, il faudrait élargir le corpus, comparer plusieurs références adaptées aux contraintes des données et mesurer la stabilité des regroupements. Pour Southern women, un modèle biparti conservant les degrés serait un contrôle complémentaire particulièrement utile.')

    page('8. Vérification du sujet et reproductibilité')
    p('La vérification distingue les livrables exigés du niveau de preuve apporté par les expériences. Le sujet demande une implémentation, une documentation des commandes, un fichier Bash et un rapport d’environ dix pages. Il exige aussi le comptage de motifs non orientés à quatre sommets au minimum, un modèle de configuration et une application à plusieurs types de réseaux réels.')
    table(['Exigence du sujet', 'État et élément vérifiable'], [
        ['Rapport d’environ 10 pages', 'Présent rapport : exactement 10 pages, références incluses.'],
        ['Implémentation', 'src/superfamilies.py ; Python, sans étape de compilation.'],
        ['Commandes dans un fichier Bash', 'run_experiments.sh : préparation, tests, trois expériences et comparaison.'],
        ['Documentation des options', 'README.md et aide --help.'],
        ['Motifs à 4 sommets, non orientés', 'Six graphlets connexes induits ; vérification indépendante exhaustive.'],
        ['Configuration et SRP', 'Ensemble simple à degrés fixés approché par échanges ; formule de [1], epsilon = 4.'],
        ['Plusieurs types de graphes réels', 'Relations sociales, affiliations et réseaux trophiques ; réseau littéraire complémentaire.'],
        ['Étude des superfamilles', 'Comparaison des profils et sensibilité ; conclusions exploratoires.']], [165, 310])
    h('Validation du programme')
    p('Dix tests automatisés vérifient les six motifs isolés, les graphes non connexes, le comptage sur tout le catalogue de petits graphes, la conservation des degrés, la formule numérique, la répétabilité, les paramètres invalides, la préservation du graphe d’entrée et le signalement des échanges incomplets. Ils passent dans l’environnement utilisé pour produire ce rapport.')
    version = next(iter(results.values()))['versions']
    p(f"Les résultats ont été obtenus avec Python {version['python']} et NetworkX {version['networkx']}. Les versions sont enregistrées dans les sorties JSON. La graine seule ne garantit pas l’identité des résultats entre versions différentes des bibliothèques.")
    p('La commande bash run_experiments.sh lance les expériences depuis un environnement disposant de Python et des dépendances. Le fichier utilise des fins de ligne LF. Son exécution native sur les machines de la PPTI n’a pas été vérifiée depuis cet environnement Windows ; les commandes Python correspondantes ont été exécutées ici. Aucun Makefile n’est nécessaire pour ce programme interprété.')
    p('Le modèle choisi correspond à une configuration conditionnée à rester simple, approximée par une chaîne d’échanges. Cette convention est explicitée pour éviter de présenter la méthode comme un appariement indépendant exact de demi-arêtes. Les exigences de réalisation sont couvertes ; la portée scientifique dépend encore du corpus et du contrôle du mélange.')

    page('9. Conclusion et références')
    p('Le projet met en œuvre une chaîne complète : préparation des données, dénombrement exact des six graphlets connexes à quatre sommets, construction de graphes aléatoires à degrés fixés, calcul des SRP et comparaison des profils. Les fichiers produits permettent de retrouver les comptages observés, les comptages simulés et les paramètres de chaque expérience.')
    p('Les résultats montrent que les degrés ne résument pas toutes les différences locales entre les réseaux étudiés. Le réseau biparti, le réseau de personnages et les réseaux trophiques présentent des contraintes de construction différentes, dont le SRP révèle certains effets. La comparaison avec une référence explicite permet de décrire ces différences plus précisément qu’un simple tableau de nombres de motifs.')
    p('L’expérience ne suffit toutefois pas à retrouver une classification générale des réseaux. Elle teste la méthode sur de nouvelles données et fournit des ressemblances à approfondir. Une conclusion sur les superfamilles demanderait davantage de réseaux par domaine, des contrôles du modèle aléatoire et une évaluation de la stabilité des regroupements. C’est sur ces points que devrait porter la suite du travail.')
    h('Références')
    references = [
        '[1] R. Milo, S. Itzkovitz, N. Kashtan, R. Levitt, S. Shen-Orr, I. Ayzenshtat, M. Sheffer et U. Alon. Superfamilies of Evolved and Designed Networks. Science, 303(5663), 1538–1542, 2004. Article fourni avec le projet ; partie non orientée : p. 1541, figure 3.',
        '[2] Sujet 7 : Superfamilles de réseaux complexes. Énoncé AAGA fourni dans projet_superfamilies.pdf, une page. Les attendus de réalisation et de contenu sont vérifiés à la page 9 du présent rapport.',
        '[3] NetworkX. Jeux de données et générateurs : karate_club_graph, florentine_families_graph, davis_southern_women_graph, les_miserables_graph. Documentation : https://networkx.org/documentation/stable/reference/generators/social.html ; version utilisée enregistrée dans les résultats.',
        '[4] E. Calò. Food webs: edge lists and species names, version 1. Zenodo, 2025. https://doi.org/10.5281/zenodo.15045517. Fichiers et références empiriques archivés dans data/. Consultation : 10 novembre 2026.',
        '[5] NetworkX. double_edge_swap : échanges d’arêtes préservant les degrés. https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.swap.double_edge_swap.html. L’implémentation utilisée est celle de la version enregistrée dans les résultats.',
    ]
    for reference in references:
        p(reference)
    h('Fichiers permettant de reprendre le travail')
    p('rapport.md fournit une version éditable du texte. src/build_report.py régénère le PDF à partir des résultats. results/results.json et profiles.csv contiennent les valeurs de l’expérience principale ; les sous-dossiers seed43/ et swaps20/ contiennent les contrôles. Le bilan détaillé des exigences est également disponible dans VERIFICATION.md.')

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#bac9d2'))
        canvas.line(48, 43, A4[0] - 48, 43)
        canvas.setFont('Body', 8)
        canvas.setFillColor(colors.HexColor('#52616b'))
        canvas.drawString(48, 29, 'AAGA — Superfamilles de réseaux complexes')
        canvas.drawRightString(A4[0] - 48, 29, f'{doc.page} / 10')
        canvas.restoreState()

    doc = SimpleDocTemplate(str(ROOT / 'rapport.pdf'), pagesize=A4,
                            rightMargin=60, leftMargin=60, topMargin=48, bottomMargin=58,
                            title='Superfamilles de réseaux complexes — Projet AAGA',
                            author='', subject='Graphlets, modèle de configuration et profils SRP')
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    reader = PdfReader(ROOT / 'rapport.pdf')
    assert len(reader.pages) == 10, f'Expected 10 pages, obtained {len(reader.pages)}'
    (ROOT / 'rapport.md').write_text('\n'.join(markdown), encoding='utf-8')
    print('rapport.pdf : 10 pages ; rapport.md : source éditable.')


if __name__ == '__main__':
    main()

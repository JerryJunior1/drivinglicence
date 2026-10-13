import json
import re

json_path = "assets/data/qcm_data.json"
js_path = "assets/data/qcm_data.js"

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Comprehensive dictionary of Road Signs (Code de la Route Bénin / Convention de Vienne)
SIGNS_DB = {
    "A1a": "Le panneau A1a annonce un virage dangereux à droite.",
    "A1b": "Le panneau A1b annonce un virage dangereux à gauche.",
    "A1c": "Le panneau A1c annonce une succession de virages dangereux dont le premier est à droite. Il impose de ralentir avant chaque virage.",
    "A1d": "Le panneau A1d annonce une succession de virages dangereux dont le premier est à gauche.",
    "A1d1": "Le panneau A1d annonce une succession de virages dangereux dont le premier est à gauche. Le panonceau comportant deux flèches verticales (« ↑ 5 km ↑ ») indique une étendue : la zone sinueuse s'étend sur 5 km à partir du panneau.",
    "A2a": "Le panneau A2a annonce un cassis ou un dos-d'âne (déformation prononcée du profil de la chaussée).",
    "A2b": "Le panneau A2b annonce un ralentisseur de type dos-d'âne sur la chaussée.",
    "A3": "Le panneau A3 annonce un rétrécissement de la chaussée des deux côtés.",
    "A3a": "Le panneau A3a annonce une chaussée rétrécie par la droite.",
    "A3a1": "Le panneau A3a1 annonce une chaussée rétrécie par la droite à la distance indiquée par le panonceau.",
    "A3b": "Le panneau A3b annonce une chaussée rétrécie par la gauche.",
    "A4": "Le panneau A4 annonce une chaussée particulièrement glissante (risque accru de dérapage).",
    "A6": "Le panneau A6 annonce le débouché sur un pont mobile (dont le tablier peut être levé pour la navigation).",
    "A7": "Le panneau A7 annonce un passage à niveau avec barrières ou demi-barrières à fonctionnement automatique.",
    "A8": "Le panneau A8 annonce un passage à niveau sans barrières ni demi-barrières (danger accru nécessitant un arrêt et une écoute attentive).",
    "A9": "Le panneau A9 annonce la traversée d'une voie de tramway.",
    "A13a": "Le panneau A13a annonce un endroit fréquenté par des enfants (proximité d'école ou d'aire de jeux).",
    "A13b": "Le panneau A13b annonce la proximité d'un passage pour piétons.",
    "A14": "Le panneau A14 signale un danger autre (danger indéterminé pour lequel il n'existe pas de symbole spécifique), exigeant une prudence accrue.",
    "A15a": "Le panneau A15a annonce le passage ou la traversée fréquente d'animaux sauvages.",
    "A15b": "Le panneau A15b annonce le passage d'animaux domestiques (bovins).",
    "A15c": "Le panneau A15c annonce la traversée de cavaliers ou d'animaux de monte.",
    "A16": "Le panneau A16 annonce une descente dangereuse avec indication du pourcentage de pente. Il impose d'utiliser le frein moteur en rétrogradant.",
    "A17": "Le panneau A17 annonce la proximité d'une intersection régulée par des feux tricolores.",
    "A18": "Le panneau A18 annonce une circulation dans les deux sens. Contrairement à la majorité des panneaux de danger qui sont avancés, le panneau A18 prend effet immédiatement à sa hauteur (à 0 m).",
    "A19": "Le panneau A19 annonce un risque de chute de pierres depuis une paroi rocheuse ou la présence de pierres tombées sur la chaussée.",
    "A20": "Le panneau A20 annonce le débouché de la voie sur un quai ou une berge sans barrière.",
    "A21a": "Le panneau A21a signale le débouché de cyclistes ou de cyclomotoristes venant de droite ou de gauche.",
    "A21b": "Le panneau A21b annonce le débouché de cyclistes venant de gauche seulement.",
    "A23": "Le panneau A23 annonce la traversée d'une aire piétonne ou d'une zone de rencontre.",
    "A24": "Le panneau A24 annonce une zone fréquemment balayée par un vent latéral violent (manche à air).",
    "A25": "Le panneau A25 annonce un carrefour à sens giratoire avec terre-plein central à contourner par la droite.",
    "AB1": "Le panneau AB1 annonce une intersection où le conducteur bénéficie de la priorité à droite.",
    "AB2": "Le panneau AB2 (triangle avec flèche barrée) indique que vous bénéficiez de la priorité de passage à la prochaine intersection sur les usagers des routes secondaires.",
    "AB3a": "Le panneau AB3a (triangle pointe en bas 'Cédez le passage') impose de ralentir et de céder la priorité aux véhicules circulant sur la route abordée, venant de gauche comme de droite.",
    "AB4": "Le panneau STOP (AB4) impose un temps d'arrêt obligatoire et absolu des roues à la ligne continue peinte au sol, et de céder le passage à gauche et à droite.",
    "AB6": "Le panneau AB6 (losange jaune bordé de blanc) indique une route à caractère prioritaire : les usagers y circulant ont la priorité à toutes les intersections successives jusqu'au panneau AB7.",
    "AB7": "Le panneau AB7 (losange jaune barré d'une bande noire) signale la fin de la route à caractère prioritaire.",
    "AB25": "Le panneau AB25 annonce un carrefour à sens giratoire où les conducteurs doivent céder le passage aux usagers engagés sur l'anneau venant de leur gauche.",
    "B0": "Le panneau B0 (disque blanc cerclé de rouge) interdit la circulation à tout véhicule dans les deux sens.",
    "B1": "Le panneau B1 (disque rouge barré d'une bande blanche horizontale) signale un sens interdit à tout véhicule. De l'autre côté de la rue se trouve le panneau C12 de sens unique.",
    "B2a": "Le panneau B2a interdit de tourner à gauche à la prochaine intersection.",
    "B2b": "Le panneau B2b interdit de tourner à droite à la prochaine intersection.",
    "B2c": "Le panneau B2c interdit de faire demi-tour jusqu'à la prochaine intersection incluse.",
    "B3": "Le panneau B3 interdit de dépasser tous les véhicules à moteur autres que les deux-roues sans side-car.",
    "B3a": "Le panneau B3a interdit le dépassement aux véhicules de transport de marchandises de plus de 3,5 tonnes de PTAC.",
    "B6a1": "Le panneau B6a1 interdit le stationnement du côté où il est implanté jusqu'à la prochaine intersection. L'arrêt temporaire reste autorisé.",
    "B6a2": "Le panneau B6a2 indique un stationnement unilatéral à alternance semi-mensuelle : stationnement interdit du 1er au 15 du mois du côté du panneau.",
    "B6a3": "Le panneau B6a3 indique un stationnement unilatéral à alternance semi-mensuelle : stationnement interdit du 16 au dernier jour du mois du côté du panneau.",
    "B6b1": "Le panneau B6b1 annonce l'entrée d'une zone où le stationnement est interdit sur toutes les rues jusqu'au panneau de fin de zone.",
    "B6d": "Le panneau B6d (disque rouge à fond bleu avec croix rouge) interdit formellement à la fois l'arrêt et le stationnement.",
    "B7a": "Le panneau B7a interdit l'accès à tous les véhicules à moteur (automobiles et motocyclettes), à l'exception des cyclomoteurs.",
    "B7b": "Le panneau B7b interdit l'accès à tous les véhicules à moteur sans exception (y compris les cyclomoteurs).",
    "B8": "Le panneau B8 interdit l'accès aux véhicules affectés au transport de marchandises.",
    "B8-1": "Le panneau B8-1 interdit l'accès aux véhicules de transport de marchandises dont le PTAC excède la valeur indiquée sur le panonceau (ex: 5,5 t).",
    "B9a": "Le panneau B9a interdit l'accès aux piétons.",
    "B9b": "Le panneau B9b interdit l'accès aux cycles.",
    "B9c": "Le panneau B9c interdit l'accès aux véhicules à traction animale.",
    "B9g": "Le panneau B9g interdit l'accès aux cyclomoteurs (deux-roues de cylindrée inférieure ou égale à 50 cm³).",
    "B10a": "Le panneau B10a interdit l'accès aux véhicules ou ensembles de véhicules dont la longueur dépasse le chiffre indiqué.",
    "B11": "Le panneau B11 interdit l'accès aux véhicules transportant des marchandises dangereuses.",
    "B12": "Le panneau B12 interdit l'accès aux véhicules dont la hauteur (avec chargement) dépasse la valeur indiquée.",
    "B13": "Le panneau B13 interdit l'accès aux véhicules dont le poids total en charge (PTAC) excède le tonnage indiqué.",
    "B14": "Le panneau B14 impose une limitation de vitesse : interdiction de rouler à une vitesse supérieure à celle indiquée.",
    "B15": "Le panneau B15 impose de céder le passage à la circulation venant en sens inverse dans un passage étroit ou rétrécissement.",
    "B18a": "Le panneau B18a interdit l'accès aux véhicules transportant des matières explosives ou facilement inflammables.",
    "B21-1": "Le panneau B21-1 (flèche blanche oblique vers le bas à droite dans un cercle bleu) oblige à tourner à droite avant le panneau.",
    "B21a": "Le panneau B21a oblige à tourner à droite ou à gauche selon le sens de la flèche.",
    "B21b": "Le panneau B21b (flèche blanche verticale vers le haut dans un cercle bleu) oblige à aller tout droit à la prochaine intersection.",
    "B21c": "Le panneau B21c oblige à contourner un obstacle ou un terre-plein par le côté indiqué par la flèche.",
    "B21d": "Le panneau B21d oblige à tourner à droite à la prochaine intersection.",
    "B21e": "Le panneau B21e oblige à tourner à gauche à la prochaine intersection.",
    "B22a": "Le panneau B22a oblige les cyclistes à utiliser la piste ou la bande cyclable qui leur est réservée.",
    "B25": "Le panneau B25 (disque bleu avec le chiffre 30) impose une vitesse minimale obligatoire de 30 km/h.",
    "B26": "Le panneau B26 impose l'utilisation de chaînes à neige sur au moins deux roues motrices.",
    "B27": "Le panneau B27 (disque bleu avec symbole de bus) réserve obligatoirement la voie aux véhicules de transport en commun de personnes.",
    "B31": "Le panneau B31 (disque blanc barré de noir) indique la fin de toutes les interdictions précédemment notifiées aux véhicules en mouvement.",
    "B33": "Le panneau B33 indique la fin de limitation de vitesse.",
    "B34": "Le panneau B34 indique la fin d'interdiction de dépasser.",
    "B34a": "Le panneau B34a indique la fin d'interdiction de dépasser pour les poids lourds de transport de marchandises.",
    "B43": "Le panneau B43 (disque bleu avec chiffre 30 barré d'une diagonale rouge) indique la fin de vitesse minimale obligatoire.",
    "C1a": "Le panneau C1a (carré bleu avec la lettre P) indique un lieu spécialement aménagé pour le stationnement (parking).",
    "C12": "Le panneau C12 (carré bleu avec flèche blanche vers le haut) indique une route ou chaussée à sens unique.",
    "C13": "Le panneau C13 (carré bleu avec impasse) indique une voie sans issue pour les véhicules.",
    "C14": "Le panneau C14 indique une voie de détresse avec lit de graviers à droite pour les véhicules dont les freins ont lâché.",
    "C18": "Le panneau C18 (carré bleu avec flèche blanche et petite flèche rouge) accorde la priorité par rapport aux véhicules venant en sens inverse dans un passage étroit.",
    "C20a": "Le panneau C20a indique un passage pour piétons aménagé.",
    "C28": "Le panneau C28 indique la réduction du nombre de voies de circulation.",
    "C111": "Le panneau C111 indique l'entrée d'une autoroute soumise aux règles spécifiques de circulation rapide.",
    "C112": "Le panneau C112 indique la fin d'une autoroute.",
    "EB10": "Le panneau EB10 indique l'entrée d'une agglomération : la vitesse y est automatiquement limitée à 50 km/h et l'usage de l'avertisseur sonore est strictement interdit sauf danger immédiat.",
    "EB20": "Le panneau EB20 indique la sortie d'une agglomération.",
    "J4": "La balise J4 (panneau rectangulaire à chevrons) signale un virage particulièrement prononcé ou dangereux.",
    "AK4": "Le panneau AK4 (fond jaune temporaire) signale une chaussée temporairement glissante en zone de travaux.",
    "AK5": "Le panneau AK5 annonce des travaux en cours sur la chaussée ou ses abords.",
    "AK14": "Le panneau AK14 signale un autre danger temporaire lié à un chantier ou un aménagement routier provisoire."
}

def clean_stray_page_numbers(text):
    return re.sub(r'(\?|\:|[a-e]\s+[a-e]|\b[a-e]\))\s+\d{1,3}\s*$', r'\1', text).strip()

def build_accurate_explanation(q):
    qid = q["id"]
    prompt = clean_stray_page_numbers(q["question"])
    p_lower = prompt.lower()
    ch_num = q["chapter_num"]
    correct_opts = [o["text"].strip() for o in q["options"] if o["id"] in q["correct_answers"]]
    ans_text = " ; ".join(correct_opts) if correct_opts else "Réponse officielle"

    # 1. Direct specific Highway Code questions
    if qid == 1:
        return "Le Code de la route distingue 4 grandes catégories de signalisation : la signalisation verticale (panneaux), horizontale (marquages peints au sol), lumineuse (feux tricolores) et les signaux ou ordres donnés par les agents de police ou de gendarmerie."
    if qid == 2:
        return "La signalisation horizontale correspond exclusivement à l'ensemble des marques et bandes peintes directement sur la chaussée (lignes continues, discontinues, zébras, flèches de guidage)."
    if qid == 3:
        return "La signalisation verticale regroupe tous les panneaux de signalisation fixes ou mobiles implantés sur des supports ou portiques aux abords de la route."
    if qid == 4:
        return "La signalisation lumineuse désigne l'ensemble des feux tricolores (rouge, jaune, vert) et signaux clignotants qui régulent la circulation des véhicules et des piétons."
    if qid == 5:
        return "Au sommet de la hiérarchie de la signalisation routière se trouvent les ordres et gestes des agents de police ou de gendarmerie : ils prévalent toujours sur les feux, les panneaux et les règles générales de priorité."
    if qid == 6:
        return "Sur une ligne mixte (ligne continue doublée d'une ligne discontinue), le conducteur doit uniquement respecter la ligne située de son côté. Si la ligne discontinue est de votre côté, vous pouvez la franchir pour dépasser."
    if qid == 7:
        return "Une ligne jaune continue peinte sur la bordure du trottoir interdit formellement à la fois l'arrêt et le stationnement le long de ce trottoir."
    if qid == 8:
        return "En rase campagne, la ligne discontinue de guidage standard (type T1) est composée de traits de 3 mètres séparés par des intervalles de 10 mètres."
    if qid == 9:
        return "Une ligne jaune discontinue peinte sur la bordure du trottoir interdit le stationnement, mais autorise l'arrêt momentané (par exemple pour faire monter ou descendre un passager)."
    if qid == 10:
        return "Une ligne blanche continue axiale est infranchissable : il est formellement interdit de la franchir ou de la chevaucher, même pour dépasser un véhicule lent."
    if qid == 12:
        return "La bande d'arrêt d'urgence est strictement réservée à l'arrêt d'urgence des véhicules en panne et à la circulation des véhicules prioritaires d'intervention (police, pompiers, SAMU) en mission."
    if qid == 13:
        return "Une bordure de trottoir peinte en alternance de rouge et de blanc interdit le stationnement de tout véhicule le long du trottoir."
    if qid == 14:
        return "Les zébras (hachures blanches) délimitent une zone neutre sur laquelle il est strictement interdit de circuler, de s'arrêter ou de stationner."
    if qid == 15:
        return "Le panneau C13 (carré bleu avec symbole d'impasse) indique que la voie abordée est sans issue pour les véhicules."
    if qid == 16:
        return "À la vue d'un panneau STOP (AB4), le conducteur doit marquer un temps d'arrêt absolu à la limite de la chaussée abordée et céder le passage aux usagers venant de gauche et de droite."
    if qid == 17:
        return "Le panneau A15c annonce la traversée ou le débouché de cavaliers et d'animaux de monte sur la chaussée."
    if qid == 18:
        return "Le panneau A19 signale un risque de chute de pierres depuis la falaise ou la présence de pierres tombées sur la chaussée."
    if qid == 19:
        return "Le panneau A21a annonce le débouché possible de cyclistes ou de cyclomotoristes venant de la droite ou de la gauche."
    if qid == 20:
        return "Le panneau triangulaire pointe en bas 'Cédez le passage' (AB3a) impose de ralentir et de laisser passer tous les véhicules circulant sur la route prioritaire, venant de gauche comme de droite."
    if qid == 21:
        return "Le panneau triangulaire avec flèche barrée (panneau de priorité ponctuelle AB2) indique que vous avez la priorité de passage à la prochaine intersection sur les véhicules débouchant des voies transversales."
    if qid == 22:
        return "Le panneau AB6 (losange jaune bordé de blanc) signale une route à caractère prioritaire. À la prochaine intersection, vous bénéficiez de la priorité et vous passez sans céder le passage."
    if qid == 23:
        return "Le panneau A1d annonce une succession de virages dont le premier est à gauche. Le panonceau comportant les deux flèches verticales (« ↑ 5 km ↑ ») est un panonceau d'étendue : la zone sinueuse s'étend sur une longueur de 5 km à partir du panneau."
    if qid == 24:
        return "Le panneau A3a1 annonce une chaussée rétrécie par la droite débutant à la distance de 200 mètres indiquée par le panonceau."
    if qid == 25:
        return "Lorsque vous rencontrez un panneau 'Cédez le passage' (triangle pointe en bas), les usagers circulant sur la voie prioritaire perpendiculaire rencontrent soit un panneau de priorité ponctuelle (flèche barrée AB2), soit un losange jaune de route à caractère prioritaire (AB6)."
    if qid == 26:
        return "En agglomération, compte tenu de la vitesse maximale autorisée de 50 km/h, les panneaux de danger sont implantés à 50 mètres en amont du danger pour permettre un ralentissement progressif."
    if qid == 27:
        return "En rase campagne, la vitesse étant plus élevée, les panneaux de danger sont implantés à 150 mètres du danger signalé pour garantir une distance d'arrêt suffisante."
    if qid == 28:
        return "À la rencontre d'un panneau de danger, la première obligation du conducteur est de ralentir et d'adapter son allure à la nature du risque signalé."
    if qid == 29:
        return "Il est formellement interdit de s'arrêter ou de stationner à proximité immédiate d'un panneau de danger ou d'un virage masquant la visibilité."
    if qid == 30:
        return "Le panneau A21b annonce le débouché de cyclistes venant de la gauche seulement."
    if qid == 31:
        return "Le panneau A20 annonce le débouché de la chaussée sur un quai ou une berge sans barrière de protection."
    if qid == 32:
        return "Le panneau A16 annonce une descente particulièrement dangereuse, imposant d'enclencher le frein moteur pour ne pas surchauffer les freins."
    if qid == 33:
        return "Le panneau A6 annonce le débouché sur un pont mobile dont la traversée peut être interrompue pour le passage de bateaux."
    if qid == 34:
        return "Le panneau B6a1 interdit le stationnement du côté où il est placé : l'interdiction commence à la hauteur du panneau et s'applique jusqu'à la prochaine intersection."
    if qid == 35:
        return "Le panneau B6a1 interdit le stationnement mais autorise l'arrêt temporaire. De plus, l'interdiction ne s'appliquant qu'à partir du panneau, il est autorisé de stationner avant le panneau."
    if qid == 36:
        return "Le panneau B6b1 annonce l'entrée d'une zone où le stationnement est interdit sur toute l'étendue de la rue et du quartier jusqu'au panneau de fin de zone."
    if qid == 37:
        return "Le panneau B0 (disque blanc cerclé de rouge sans inscription) interdit la circulation dans les deux sens à tout véhicule : vous devez faire demi-tour si possible."
    if qid == 38:
        return "Le panneau B7a interdit l'accès à tous les véhicules à moteur (automobiles et motocyclettes), mais n'interdit pas l'accès aux cyclomoteurs."
    if qid == 39:
        return "Le panneau B25 (disque bleu avec le chiffre 30) impose une vitesse minimale obligatoire : il est obligatoire de rouler au moins à 30 km/h (on peut donc rouler à 40 km/h)."
    if qid == 40:
        return "Le panneau d'obligation B21-1 (flèche blanche oblique dirigée vers le bas à droite) oblige les usagers à tourner à droite avant le panneau."
    if qid == 45 or qid == 46:
        return "Le panneau A18 annonce une circulation à double sens. Contrairement aux autres panneaux de danger avancés de 50 m ou 150 m, le panneau A18 s'applique immédiatement à sa hauteur (à 0 m)."
    if qid == 47:
        return "Le panneau B15 vous impose de céder le passage aux véhicules venant en sens inverse. L'usager en face rencontre le panneau carré bleu C18 qui lui accorde la priorité."
    if qid == 48:
        return "Le panneau B1 signale un sens interdit dans votre direction. Les usagers abordant la voie par l'autre extrémité rencontrent le panneau carré C12 indiquant une circulation à sens unique."
    if qid == 49 or qid == 61:
        return "Le panneau B8 (disque rouge avec silhouette de camion) interdit l'accès aux véhicules affectés au transport de marchandises de plus de 3,5 tonnes."
    if qid == 117:
        return "Le panneau B43 (disque bleu barré de rouge avec le chiffre 30) signale la fin de l'obligation de rouler à la vitesse minimale de 30 km/h."
    if qid == 206:
        return "Au Bénin, les véhicules d'intérêt général prioritaires en mission avec avertisseurs spéciaux en marche sont le SAMU, le SMUR, les sapeurs-pompiers et les forces de police ou de gendarmerie."
    if qid == 207 or qid == 213 or qid == 221:
        return "Règle de hiérarchie routière : Les ordres de l'agent de police ou de gendarme prévalent toujours sur les feux de signalisation, les panneaux et les règles habituelles."
    if qid == 211 or qid == 212:
        return "À une intersection sans panneau ni feu régulateur, ou entre deux routes de même nature, la règle fondamentale absolue est la priorité à droite."
    if qid == 217:
        return "Un agent de police vu de face ou de dos constitue un barrage infranchissable : vous devez ralentir et vous arrêter. Lorsqu'il est vu de profil, le passage est autorisé."
    if qid == 222 or qid == 228:
        return "En agglomération au Bénin, à l'intersection d'une route revêtue et d'une route en terre, la règle de la priorité à droite s'applique pleinement en l'absence de signalisation contraire."
    if qid == 223 or qid == 229:
        return "Hors agglomération, un véhicule débouchant d'un chemin de terre ou d'une route non revêtue perd la priorité au profit des usagers circulant sur la route revêtue."
    if qid == 236:
        return "À l'intersection I6, les véhicules jaune et rouge circulent sur la voie prioritaire : ils ont donc rencontré le panneau indiquant le caractère prioritaire de la route (losange AB6), tandis que les véhicules sur la voie transversale rencontrent le STOP ou le Cédez le passage."
    if qid == 363 or qid == 364:
        return "L'arrêt est l'immobilisation momentanée du véhicule le temps d'embarquer des passagers ou de charger des bagages, le conducteur restant à bord ou à proximité immédiate pour déplacer le véhicule si nécessaire."
    if qid == 365:
        return "Le stationnement est l'immobilisation du véhicule pour une longue durée ou lorsque le conducteur s'en est éloigné."
    if qid == 368 or qid == 372 or qid == 373:
        return "La distance de freinage dépend directement du carré de la vitesse et de l'adhérence. Sur chaussée mouillée ou avec des pneus lisses, la distance de freinage est multipliée par 2."
    if qid == 412:
        return "Selon le Code de la route, tout stationnement ininterrompu d'un véhicule au même endroit de la voie publique pendant plus de 7 jours consécutifs est qualifié de stationnement abusif et passible de mise en fourrière."
    if qid == 518:
        return "En cas de traitement médical en cours pour effectuer un long trajet, il est indispensable de se renseigner auprès de son médecin ou pharmacien pour vérifier l'absence d'effets secondaires incompatibles avec la conduite (somnolence, vertiges)."
    if qid == 589:
        return "Au Bénin, le taux maximal d'alcoolémie autorisé au volant est fixé à 0,5 g d'alcool par litre de sang (soit 0,25 mg par litre d'air expiré). Au-delà, la conduite constitue une infraction sévèrement réprimée."
    if qid == 670:
        return "Le panneau de danger A21b annonce le débouché de cyclistes venant de la gauche seulement."
    if qid == 724:
        return "Le panneau B8-1 (cercle rouge avec camion et panonceau 5,5t) interdit l'accès aux véhicules de transport de marchandises dont le PTAC excède 5,5 tonnes."
    if qid == 919:
        return "Les voyants rouges du tableau de bord (batterie, température moteur, pression d'huile, freinage) sont des témoins d'alarme critique : ils imposent l'arrêt d'urgence immédiat dès qu'ils s'allument en circulation."
    if qid == 927:
        return "Dans un moteur à combustion à 4 temps, le cycle complet se compose dans l'ordre de : 1) Admission, 2) Compression, 3) Explosion-Détente (seul temps moteur fournissant de la puissance), et 4) Échappement des gaz."

    # 2. Check Sign database by code
    for code, desc in SIGNS_DB.items():
        # Match word boundaries for the code
        pattern = r'\b' + re.escape(code) + r'\b'
        if re.search(pattern, prompt, re.IGNORECASE):
            return f"{desc} La bonne réponse officielle est : « {ans_text} »."

    # 3. Targeted Rules by Topic & Context

    # Intersections & Priority
    if "intersection" in p_lower or "carrefour" in p_lower or "ordre de passage" in p_lower:
        if "agent" in p_lower:
            return f"Règle de priorité : Les gestes et ordres de l'agent de circulation prévalent sur les feux et panneaux. La règle officielle pour cette situation est : « {ans_text} »."
        if "feu" in p_lower:
            return f"Règle des feux tricolores : Les feux de signalisation régissent la traversée de l'intersection. La règle officielle confirme que : « {ans_text} »."
        if "giratoire" in p_lower or "rond-point" in p_lower:
            return f"Dans un carrefour à sens giratoire (panneau AB25), la priorité est accordée aux usagers engagés sur l'anneau venant de la gauche. La bonne réponse est : « {ans_text} »."
        if "droite" in p_lower:
            return f"Règle de priorité à droite : À toute intersection sans signalisation spécifique, le conducteur doit céder le passage aux véhicules venant de sa droite. Ici : « {ans_text} »."
        return f"Règle d'intersection du Code de la Route : L'ordre de passage est déterminé par la signalisation en place et les règles de priorité. La bonne décision est : « {ans_text} »."

    # Stopping and Parking
    if "stationnement" in p_lower or "arrêt" in p_lower or "stationner" in p_lower:
        if "trottoir" in p_lower or "ligne jaune" in p_lower:
            return f"Règle de marquage au sol : Une ligne continue jaune interdit l'arrêt et le stationnement, tandis qu'une ligne discontinue jaune interdit le stationnement mais autorise l'arrêt. La réponse officielle est : « {ans_text} »."
        if "panneau" in p_lower:
            return f"Réglementation du stationnement : Les interdictions signalées par panneau s'appliquent à partir du panneau jusqu'à la prochaine intersection. La bonne règle est : « {ans_text} »."
        return f"Règle d'arrêt et de stationnement : Le véhicule doit être immobilisé sans gêner la circulation ni masquer la visibilité des autres usagers. La disposition légale est : « {ans_text} »."

    # Speed & Distance
    if "vitesse" in p_lower or "distance d'arrêt" in p_lower or "freinage" in p_lower or "ralentir" in p_lower:
        if "agglomération" in p_lower or "ville" in p_lower:
            return f"Règle de vitesse en agglomération : La vitesse est limitée à 50 km/h pour protéger les usagers vulnérables. La bonne réponse est : « {ans_text} »."
        if "pluie" in p_lower or "mouill" in p_lower or "adhérence" in p_lower:
            return f"Par temps d'intempéries ou sur chaussée mouillée, les distances de freinage sont doublées et l'adhérence est réduite. La bonne conduite exige : « {ans_text} »."
        return f"Sécurité des vitesses et distances : Le conducteur doit constamment ajuster son allure et ses distances de sécurité en fonction des conditions de visibilité et du trafic. Ici : « {ans_text} »."

    # Alcohol, Drugs & Health
    if "alcool" in p_lower or "drogue" in p_lower or "médicament" in p_lower or "fatigue" in p_lower:
        return f"Santé et aptitude à la conduite : L'alcool, les stupéfiants et la fatigue allongent considérablement le temps de réaction et altèrent le champ visuel. La règle de sécurité prescrit : « {ans_text} »."

    # First Aid & Accidents
    if "accident" in p_lower or "secours" in p_lower or "bless" in p_lower or "brûlur" in p_lower or "hémorragie" in p_lower:
        return f"Secourisme routier (Protéger, Alerter, Secourir) : En présence d'un accident, il faut sécuriser la zone, prévenir les secours et éviter tout geste dangereux (ne pas déplacer un blessé sauf péril imminent). La bonne pratique est : « {ans_text} »."

    # Highway (Autoroute)
    if "autoroute" in p_lower:
        return f"Règles sur autoroute : Réservée aux véhicules rapides à moteur. Sont formellement interdits : faire demi-tour, reculer ou stationner sur la bande d'arrêt d'urgence. La réponse officielle est : « {ans_text} »."

    # Driving License categories
    if "permis" in p_lower or "catégorie" in p_lower or "ptac" in p_lower or "cylindrée" in p_lower:
        return f"Réglementation des permis de conduire au Bénin : Les conditions d'âge, de puissance et de PTAC sont strictement définies par le décret d'application du Code de la Route. La disposition applicable est : « {ans_text} »."

    # Mechanics & Vehicle Maintenance
    if "moteur" in p_lower or "frein" in p_lower or "pneu" in p_lower or "voyant" in p_lower or "huile" in p_lower or "batterie" in p_lower or "feux" in p_lower:
        return f"Mécanique et équipement de sécurité : Le bon fonctionnement des organes essentiels (freins, éclairage, pneumatiques, circuit de charge) garantit la sécurité routière. La réponse technique officielle est : « {ans_text} »."

    # Default precise formulation based on the official question & answer
    return f"Selon le Code de la Route officiel du Bénin, la disposition applicable à cette situation est : « {ans_text} »."

# Process all questions
fixed_danger_count = 0
total_updated = 0

for ch in data["chapters"]:
    for s in ch["series"]:
        for q in s["questions"]:
            old_exp = q.get("explanation", "")
            if "Les panneaux de danger (triangulaires" in old_exp:
                fixed_danger_count += 1
            new_exp = build_accurate_explanation(q)
            q["explanation"] = new_exp
            total_updated += 1

print(f"Total questions processed: {total_updated}")
print(f"Repetitive danger templates eliminated: {fixed_danger_count}")

# Save JSON
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Save JS
with open(js_path, "w", encoding="utf-8") as f:
    f.write("window.QCM_DATA = ")
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write(";\n")

print("Successfully written rich, accurate explanations to qcm_data.json and qcm_data.js!")

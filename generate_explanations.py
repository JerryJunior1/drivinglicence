import json
import re
import os

data_path = "assets/data/qcm_data.json"
with open(data_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Rule generator engine for Highway Code (Benin & West Africa / Vienna Convention)
def generate_explanation(q):
    q_id = q["id"]
    ch_num = q["chapter_num"]
    prompt = q["question"]
    correct_letters = q["correct_answers"]
    
    # Get text of correct options
    correct_texts = [opt["text"] for opt in q["options"] if opt["id"] in correct_letters]
    correct_summary = " ; ".join(correct_texts)
    
    p_lower = prompt.lower()
    
    # Specific known questions & core rules:
    if q_id == 1:
        return "Le Code de la route distingue 4 grandes catégories de signalisation : la signalisation verticale (les panneaux), la signalisation horizontale (les marquages au sol), la signalisation lumineuse (les feux) et les ordres donnés par les agents de sécurité routière (qui priment sur toutes les autres)."
    if q_id == 2:
        return "La signalisation horizontale correspond exclusivement aux marques, lignes et symboles peints directement sur la chaussée pour guider la circulation."
    if q_id == 3:
        return "La signalisation verticale regroupe tous les panneaux de signalisation implantés sur des poteaux ou portiques en bordure de route."
    if q_id == 4:
        return "La signalisation lumineuse désigne l'ensemble des feux tricolores (rouge, jaune/orange, vert) et des signaux lumineux temporaires qui régulent les carrefours et zones de travaux."
    if q_id == 5:
        return "Les ordres et gestes des agents de la police et de la gendarmerie sont au sommet de la hiérarchie routière : ils prévalent toujours sur les feux, les panneaux et les règles habituelles."
    if q_id == 6:
        return "Sur une ligne mixte, le conducteur doit uniquement respecter la ligne la plus proche de sa voie. Si la ligne discontinue est de votre côté, le dépassement est autorisé ; si c'est la ligne continue, il est interdit."
    if q_id == 7:
        return "Une ligne jaune continue peinte sur la bordure d'un trottoir interdit formellement à la fois l'arrêt et le stationnement de tout véhicule."
    if q_id == 8:
        return "Sur route en rase campagne, l'intervalle standard entre deux traits d'une ligne discontinue blanche centrale (type T1) est de 10 mètres pour 3 mètres de trait plein."
    if q_id == 9:
        return "Une ligne jaune discontinue peinte sur la bordure du trottoir interdit le stationnement, mais autorise l'arrêt temporaire (par exemple pour faire monter ou descendre un passager)."
    if q_id == 10:
        return "Une ligne blanche continue dans l'axe de la chaussée est infranchissable : il est strictement interdit de la couper ou de la chevaucher, même pour dépasser."
    if q_id == 12:
        return "La bande d'arrêt d'urgence est réservée aux véhicules prioritaires en mission urgente (ambulances, pompiers, forces de l'ordre) et aux véhicules d'entretien, ou en cas de panne absolue d'un usager."
    if q_id == 13:
        return "Une alternance de rouge et de blanc le long du trottoir signale une interdiction de stationner le long de cette bordure."
    if q_id == 14:
        return "Les zébras (hachures blanches) délimitent un espace neutre sur lequel il est formellement interdit de circuler, de s'arrêter ou de stationner."
    if q_id == 15:
        return "Le panneau carré à fond bleu C13 indique une impasse (voie sans issue pour les véhicules)."
    if q_id == 16:
        return "Devant un panneau STOP (AB4), le marquage au sol impose l'arrêt absolu des roues à la limite de la chaussée abordée, et de céder le passage à tous les usagers venant de droite comme de gauche."
    if q_id == 17:
        return "Le panneau A15c annonce un danger : le débouché ou la présence d'animaux domestiques ou de cavaliers sur la chaussée."
    if q_id == 18:
        return "Le panneau A19 indique un risque de chute de pierres depuis la paroi rocheuse ou la présence de pierres tombées sur la chaussée."
    if q_id == 19:
        return "Le panneau A21a signale le débouché possible de cyclistes ou de cyclomotoristes venant de la droite ou de la gauche."
    if q_id == 20:
        return "Le panneau triangulaire pointe en bas 'Cédez le passage' (AB3a) impose de ralentir et de céder la priorité aux véhicules circulant sur la voie prioritaire, venant de gauche comme de droite."
    if q_id == 206:
        return "Au Bénin, les véhicules prioritaires lorsqu'ils utilisent leurs avertisseurs sonores et lumineux sont les services de secours médical (SAMU, SMUR), les sapeurs-pompiers, la police et la gendarmerie en mission."
    if q_id == 207:
        return "Même si le feu tricolore fonctionne, les injonctions de l'agent de police ou de gendarme priment impérativement sur la signalisation lumineuse."
    if q_id == 211:
        return "En l'absence totale de signalisation (ni panneau, ni feu, ni marquage), la règle générale absolue du Code de la route est la priorité à droite."
    if q_id == 212:
        return "À l'intersection de deux routes de même nature sans panneau, la priorité à droite s'applique sans exception."
    if q_id == 356:
        return "Sur cette image d'intersection (Im 6), l'ordre de passage est déterminé par l'autorité de l'agent de police qui régule la circulation et autorise les véhicules selon l'orientation de ses bras."
    if q_id == 363 or q_id == 364:
        return "L'arrêt est l'immobilisation momentanée du véhicule le temps de faire monter ou descendre des personnes ou de charger/décharger des objets, le conducteur devant rester à bord ou à proximité immédiate pour pouvoir le déplacer en cas de besoin."
    if q_id == 365:
        return "Le stationnement est l'immobilisation prolongée du véhicule pour une raison autre que la montée/descente de passagers ou le chargement, le conducteur ayant quitté son véhicule."
    if q_id == 584 or q_id == 588:
        return "L'alcool altère gravement les facultés de conduite : il rétrécit le champ visuel, réduit la vigilance, fausse l'estimation des distances et allonge le temps de réaction."
    if q_id == 589:
        return "Au Bénin et selon les standards de sécurité routière, le seuil d'alcoolémie légal à partir duquel la conduite devient répréhensible est fixé à 0,5 g d'alcool par litre de sang."
    if q_id == 646:
        return "Sur une motocyclette, le passager doit être assis sur une selle double ou un siège arrière fixe, les pieds sur les repose-pieds, et faire corps avec la machine et le conducteur pour stabiliser la trajectoire."
    if q_id == 676 or q_id == 677:
        return "Le permis moto A2 autorise la conduite de motocyclettes d'une cylindrée maximale de 400 cm³ dès l'âge de 18 ans."
    if q_id == 679 or q_id == 688 or q_id == 689:
        return "Pour les véhicules légers (Permis B) ou poids lourds (Permis C1/C), les conditions d'âge minimal et de PTAC sont strictement définies par le décret portant réglementation du permis de conduire au Bénin."
    if q_id == 925:
        return "À l'avant d'un véhicule automobile de tourisme, les feux obligatoires comprennent au minimum deux feux de route (phares), deux feux de croisement (codes), deux feux de position et deux indicateurs de direction (clignotants)."
    if q_id == 927:
        return "Dans un moteur à explosion à 4 temps, le cycle thermodynamique se déroule toujours dans l'ordre suivant : 1) Admission, 2) Compression, 3) Explosion/Détente, 4) Échappement."

    # Pattern-based explanations:
    if "agent" in p_lower and ("priorité" in p_lower or "prévaut" in p_lower or "feu" in p_lower):
        return f"Règle fondamentale : Les injonctions et gestes des agents de sécurité routière (police, gendarmerie) prévalent systématiquement sur les feux tricolores, les panneaux et le marquage au sol. La bonne réponse est : {correct_summary}."
    
    if "priorit" in p_lower and ("droite" in p_lower or "intersection" in p_lower or "carrefour" in p_lower):
        return f"En matière de priorité, la règle fondamentale à toute intersection sans indication contraire est la priorité aux usagers arrivant par votre droite. Ici, la règle officielle confirme que : {correct_summary}."

    if "panneau" in p_lower and ("a" in p_lower or "danger" in p_lower):
        return f"Les panneaux de danger (triangulaires à fond blanc ou jaune et bord rouge) annoncent un risque potentiel en amont. En rase campagne, ils sont placés à 150 m du danger et en agglomération à 50 m. Ici : {correct_summary}."

    if "panneau" in p_lower and ("b" in p_lower or "interdiction" in p_lower or "obligation" in p_lower):
        return f"Les panneaux de prescription absolue (ronds) imposent une règle immédiate dès la hauteur du panneau : les ronds rouges interdisent, les ronds bleus obligent. Ici : {correct_summary}."

    if "stationnement" in p_lower or "arrêt" in p_lower:
        return f"Règle du Code : Le stationnement ou l'arrêt ne doit jamais gêner la visibilité ni bloquer le passage des autres usagers ou des véhicules de secours. La disposition légale applicable est : {correct_summary}."

    if "vitesse" in p_lower or "autoroute" in p_lower or "agglomération" in p_lower:
        return f"Les limitations de vitesse protègent la sécurité de tous : 50 km/h en agglomération, et une vitesse adaptée aux conditions météorologiques et à la visibilité (50 km/h en cas de visibilité inférieure à 50 m). La réponse officielle est : {correct_summary}."

    if "alcool" in p_lower or "sécurité" in p_lower or "accident" in p_lower or "ceinture" in p_lower:
        return f"Dispositions de sécurité routière : Le respect de ces précautions est obligatoire pour préserver la vie des occupants et des tiers. La règle impose que : {correct_summary}."

    if "permis" in p_lower or "ptac" in p_lower or "catégorie" in p_lower:
        return f"Réglementation des titres de conduite au Bénin : Les catégories de permis sont délimitées en fonction de l'âge minimal, du PTAC du véhicule et du nombre de passagers autorisés. La prescription officielle est : {correct_summary}."

    if "moteur" in p_lower or "frein" in p_lower or "pneu" in p_lower or "feux" in p_lower or "huile" in p_lower:
        return f"Entretien et sécurité mécanique : Le bon état technique du véhicule et de ses organes de sécurité (freinage, suspension, éclairage, pneumatiques) est impératif pour circuler en toute légalité. Ici : {correct_summary}."

    # General well-formulated fallback based on the official text
    return f"Selon les dispositions officielles du Code de la Route du Bénin, la bonne réponse est « {correct_summary} ». Cette règle vise à assurer la fluidité de la circulation et la sécurité de l'ensemble des usagers de la route."

# Apply to all questions
updated_count = 0
for ch in data["chapters"]:
    for s in ch["series"]:
        for q in s["questions"]:
            exp = generate_explanation(q)
            q["explanation"] = exp
            updated_count += 1

print(f"Generated explanations for {updated_count} questions.")

# Save JSON
with open(data_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Save JS wrapper
js_path = "assets/data/qcm_data.js"
with open(js_path, "w", encoding="utf-8") as f:
    f.write("window.QCM_DATA = " + json.dumps(data, ensure_ascii=False) + ";\n")

print("Saved updated data with explanations!")

import fitz
import re
import json
import os

pdf_path = "Code de route questions benin-2.pdf"
doc = fitz.open(pdf_path)

output_img_dir = "assets/images"
output_data_dir = "assets/data"
os.makedirs(output_img_dir, exist_ok=True)
os.makedirs(output_data_dir, exist_ok=True)

chapters_config = [
    {"num": "I", "title": "Généralités & Définitions", "start_page": 1, "end_page": 4},
    {"num": "II", "title": "Signalisations", "start_page": 5, "end_page": 47},
    {"num": "III", "title": "Règles de priorité, dépassement & croisement", "start_page": 48, "end_page": 97},
    {"num": "IV", "title": "Arrêt, stationnement, intégration, vitesse & manœuvres", "start_page": 98, "end_page": 106},
    {"num": "V", "title": "Route pour automobile & autoroute", "start_page": 107, "end_page": 126},
    {"num": "VI", "title": "Infractions au code de la route, incivisme & secourisme", "start_page": 127, "end_page": 155},
    {"num": "VII", "title": "Permis de conduire (Catégories A1, A2, A3)", "start_page": 156, "end_page": 161},
    {"num": "VIII", "title": "Permis de conduire (Catégorie B)", "start_page": 162, "end_page": 164},
    {"num": "IX", "title": "Permis de conduire (Catégories C & C1)", "start_page": 165, "end_page": 175},
    {"num": "X", "title": "Permis de conduire (Catégorie D)", "start_page": 176, "end_page": 188},
    {"num": "XI", "title": "Équipement, entretien & documents administratifs", "start_page": 189, "end_page": 216},
]

def get_chapter_for_page(pno):
    for ch in chapters_config:
        if ch["start_page"] <= pno <= ch["end_page"]:
            return ch
    return chapters_config[-1]

# 1. Extract course content from Chapter 1 (Pages 1 to 4)
course_sections = [
    {
        "title": "Abréviations Officielles",
        "items": [
            {"term": "TIR", "def": "Transit International Routier"},
            {"term": "TCR", "def": "Transport en Commun Restrictif"},
            {"term": "Dr", "def": "Catégorie « D » restrictif"},
            {"term": "PTAC", "def": "Poids Total Autorisé en Charge"},
            {"term": "PTRA", "def": "Poids Total Roulant Autorisé"},
            {"term": "PV", "def": "Poids à Vide"},
            {"term": "CU", "def": "Charge Utile (CU = PTAC - PV)"},
            {"term": "m", "def": "Mètre (unité de longueur)"},
            {"term": "km/h", "def": "Kilomètre par heure (vitesse)"},
            {"term": "t", "def": "Tonne (unité de poids, 1 t = 1000 kg)"}
        ]
    },
    {
        "title": "Notions et Définitions Clés",
        "items": [
            {"term": "L'Intersection de route", "def": "Lieu de jonction ou de croisement de deux ou plusieurs chaussées quels que soient le ou les angles des axes de ces chaussées."},
            {"term": "L'Autoroute", "def": "Route à deux chaussées séparées par un terre-plein central, réservée à la circulation rapide des véhicules à moteur, ne comportant pas d'intersection et accessible seulement en des points aménagés. Vitesse maximale 110 à 130 km/h (sauf indication contraire)."},
            {"term": "La Route pour automobiles", "def": "Voie rapide réservée aux véhicules motorisés, sans accès direct des riverains, avec des règles de circulation similaires à l'autoroute mais limitée à 110 km/h."},
            {"term": "Agglomération", "def": "Espace sur lequel sont groupés des immeubles bâtis rapprochés et dont l'entrée et la sortie sont signalées par des panneaux spécifiques. La vitesse y est strictement limitée à 50 km/h."}
        ]
    },
    {
        "title": "Catégories de Permis de Conduire au Bénin",
        "items": [
            {"term": "Permis A1", "def": "Motocyclettes légères dont la cylindrée ne dépasse pas 125 cm³. Âge minimum : 16 ans."},
            {"term": "Permis A2", "def": "Motocyclettes dont la cylindrée n'excède pas 400 cm³. Âge minimum : 18 ans."},
            {"term": "Permis A3", "def": "Toutes motocyclettes sans limitation de cylindrée. Âge minimum : 21 ans (ou titulaire du permis A2 depuis 2 ans)."},
            {"term": "Permis B", "def": "Véhicules affectés au transport de personnes ou marchandises de PTAC ≤ 3,5 tonnes et comportant au maximum 8 places assises (sans le conducteur). Âge minimal : 18 ans. Peut tracter une remorque de PTAC ≤ 750 kg."},
            {"term": "Permis C & C1", "def": "Véhicules de transport de marchandises dont le PTAC dépasse 3,5 tonnes. Âge minimal : 21 ans pour C, 18 ans pour C1."},
            {"term": "Permis D", "def": "Véhicules de transport en commun de personnes de plus de 8 places assises. Âge minimal : 21 ans et être titulaire du permis B depuis au moins 2 ans."}
        ]
    },
    {
        "title": "Panneaux et Signaux de Prescription Absolue",
        "items": [
            {"term": "Panneaux de Danger", "def": "Forme triangulaire, fond blanc/jaune, bordure rouge. Pointe vers le haut (sauf 'Cédez le passage' qui a la pointe vers le bas). Placé à 50m en ville, 150m en rase campagne."},
            {"term": "Panneaux d'Interdiction", "def": "Forme ronde, bordure rouge. Prennent effet immédiatement à hauteur du panneau."},
            {"term": "Panneaux d'Obligation", "def": "Forme ronde, fond bleu avec symbole blanc. Obligation immédiate."},
            {"term": "Fin d'interdiction / fin d'obligation", "def": "Forme ronde, fond blanc avec barre diagonale noire ou fond bleu barré de rouge."}
        ]
    }
]

# 2. Extract Question locations and text
PAGE_BREAK_TOKEN = "\n---PAGE_BREAK_{}--- \n"
combined_text = ""
for pno in range(4, len(doc)):
    page_num = pno + 1
    ptext = doc[pno].get_text()
    combined_text += PAGE_BREAK_TOKEN.format(page_num) + ptext

q_pattern = re.compile(r'(?:^|\n)\s*(?:Questions?\s*(?:n°|N°|n\s*°)?\s*(\d+))', re.IGNORECASE)
matches = list(q_pattern.finditer(combined_text))

raw_questions = []

for idx, match in enumerate(matches):
    q_num = int(match.group(1))
    start_pos = match.end()
    end_pos = matches[idx + 1].start() if idx + 1 < len(matches) else len(combined_text)
    
    chunk = combined_text[start_pos:end_pos]
    chunk_clean = re.sub(r'CHAPITRE\s*[-:\s]+[IVXLCDM\d]+[^\n]*', '', chunk, flags=re.IGNORECASE)
    
    page_match = re.findall(r'---PAGE_BREAK_(\d+)---', combined_text[:match.start()])
    q_page = int(page_match[-1]) if page_match else 5
    
    pages_in_chunk = [int(p) for p in re.findall(r'---PAGE_BREAK_(\d+)---', chunk)]
    all_pages = [q_page] + [p for p in pages_in_chunk if p != q_page]
    
    # Answer extraction
    ans_match = re.search(r'(R[ée]pons(?:e?s?)\s*:?[^\n]+)', chunk_clean, re.IGNORECASE)
    raw_ans = ans_match.group(1).strip() if ans_match else ""
    
    letters = []
    if raw_ans:
        ans_part = re.sub(r'r[ée]pons(?:e?s?)\s*:?', '', raw_ans, flags=re.IGNORECASE)
        letters = [l.lower() for l in re.findall(r'\b([a-eA-E])\b', ans_part)]
        
    text_before_ans = chunk_clean[:ans_match.start()] if ans_match else chunk_clean
    text_before_ans = re.sub(r'---PAGE_BREAK_\d+---', '', text_before_ans)
    
    # Options extraction
    opt_start = re.search(r'(?:^|\n)\s*([a-eA-E][\)\.-]\s*)', text_before_ans)
    
    if opt_start:
        q_prompt = text_before_ans[:opt_start.start()].strip()
        opts_raw = text_before_ans[opt_start.start():].strip()
        
        opt_matches = list(re.finditer(r'(?:^|\n)\s*([a-eA-E])[\)\.-]\s*', opts_raw))
        options = []
        for o_idx, om in enumerate(opt_matches):
            o_letter = om.group(1).lower()
            o_st = om.end()
            o_end = opt_matches[o_idx + 1].start() if o_idx + 1 < len(opt_matches) else len(opts_raw)
            o_text = opts_raw[o_st:o_end].strip()
            o_text = " ".join([l.strip() for l in o_text.splitlines() if l.strip()])
            options.append({"id": o_letter, "text": o_text})
    else:
        q_prompt = text_before_ans.strip()
        options = []
        if letters:
            max_letter = max(letters)
            all_needed = [chr(c) for c in range(ord('a'), max(ord(max_letter), ord('d')) + 1)]
            for l in all_needed:
                options.append({"id": l, "text": f"Panneau / Option {l.upper()}"})

    # Clean q_prompt: remove leading numbers, stray labels, line breaks
    q_prompt = " ".join([l.strip() for l in q_prompt.splitlines() if l.strip()])
    # Strip leading stray page/choice numbers like "1 2 3 1 2 3 97 "
    q_prompt = re.sub(r'^(?:[0-9a-e]\s+){2,}', '', q_prompt)
    q_prompt = re.sub(r'^\d+\s+', '', q_prompt)
    
    ch_info = get_chapter_for_page(q_page)

    raw_questions.append({
        "id": q_num,
        "chapter_num": ch_info["num"],
        "chapter_title": ch_info["title"],
        "page": q_page,
        "all_pages": all_pages,
        "question": q_prompt,
        "options": options,
        "raw_answer": raw_ans,
        "correct_answers": letters,
        "is_multiple_choice": len(letters) > 1,
        "images": []
    })

# 3. Spatial Image Extraction & Association
page_to_questions = {}
for q in raw_questions:
    for p in q["all_pages"]:
        if p not in page_to_questions:
            page_to_questions[p] = []
        page_to_questions[p].append(q)

images_extracted_count = 0
for pno in range(4, len(doc)):
    page_num = pno + 1
    page = doc[pno]
    img_infos = page.get_image_info(xrefs=True)
    if not img_infos:
        continue
        
    d = page.get_text("dict")
    q_starts_on_page = []
    for b in d.get("blocks", []):
        for line in b.get("lines", []):
            line_txt = "".join([s.get("text", "") for s in line.get("spans", [])]).strip()
            qm = re.search(r'Questions?\s*(?:n°|N°|n\s*°)?\s*(\d+)', line_txt, re.IGNORECASE)
            if qm:
                qn = int(qm.group(1))
                q_starts_on_page.append({"q_num": qn, "y_start": line["bbox"][1]})
                
    q_starts_on_page.sort(key=lambda x: x["y_start"])
    active_qs_on_page = [q["id"] for q in page_to_questions.get(page_num, [])]
    
    for img_idx, img in enumerate(img_infos):
        bbox = img["bbox"]
        rect = fitz.Rect(bbox)
        if rect.width < 15 or rect.height < 15:
            continue
            
        center_y = (rect.y0 + rect.y1) / 2
        target_q_num = None
        
        if q_starts_on_page:
            if center_y < q_starts_on_page[0]["y_start"] - 15:
                prev_q = q_starts_on_page[0]["q_num"] - 1
                if prev_q in active_qs_on_page or prev_q >= 1:
                    target_q_num = prev_q
            else:
                for i in range(len(q_starts_on_page)):
                    y_cur = q_starts_on_page[i]["y_start"]
                    y_next = q_starts_on_page[i+1]["y_start"] if i + 1 < len(q_starts_on_page) else page.rect.height
                    if y_cur - 25 <= center_y <= y_next + 20:
                        target_q_num = q_starts_on_page[i]["q_num"]
                        break
        elif active_qs_on_page:
            target_q_num = active_qs_on_page[0]
            
        if not target_q_num and active_qs_on_page:
            target_q_num = active_qs_on_page[0]
            
        if target_q_num:
            clip_rect = fitz.Rect(
                max(0, rect.x0 - 3),
                max(0, rect.y0 - 3),
                min(page.rect.width, rect.x1 + 3),
                min(page.rect.height, rect.y1 + 3)
            )
            pix = page.get_pixmap(clip=clip_rect, dpi=144)
            img_filename = f"q_{target_q_num}_{img_idx+1}.png"
            img_rel_path = f"assets/images/{img_filename}"
            pix.save(os.path.join(output_img_dir, img_filename))
            images_extracted_count += 1
            
            for rq in raw_questions:
                if rq["id"] == target_q_num:
                    if img_rel_path not in rq["images"]:
                        rq["images"].append(img_rel_path)
                    break

# 4. Group questions into Chapters and Series (20 questions per questionnaire)
chapters_output = []
for ch_conf in chapters_config:
    ch_num = ch_conf["num"]
    ch_qs = [q for q in raw_questions if q["chapter_num"] == ch_num]
    
    series_list = []
    chunk_size = 20
    for s_idx in range(0, len(ch_qs), chunk_size):
        chunk = ch_qs[s_idx:s_idx + chunk_size]
        s_num = (s_idx // chunk_size) + 1
        q_start_id = chunk[0]["id"]
        q_end_id = chunk[-1]["id"]
        series_id = f"ch_{ch_num.lower()}_s{s_num}"
        
        # 14/20 is the official pass threshold
        # If fewer than 20 questions, proportional >= 70%
        target_score = 14 if len(chunk) == 20 else max(1, round(len(chunk) * (14.0 / 20.0)))
        
        series_list.append({
            "series_id": series_id,
            "series_number": s_num,
            "title": f"Série {s_num}",
            "range_label": f"Questions {q_start_id} à {q_end_id}",
            "question_count": len(chunk),
            "pass_score": target_score,
            "pass_threshold_text": f"{target_score}/{len(chunk)}",
            "questions": chunk
        })
        
    chapters_output.append({
        "id": ch_num,
        "title": ch_conf["title"],
        "start_page": ch_conf["start_page"],
        "end_page": ch_conf["end_page"],
        "total_questions": len(ch_qs),
        "total_series": len(series_list),
        "series": series_list
    })

full_data = {
    "metadata": {
        "title": "Code de la Route Bénin - Entraînement QCM Officiel",
        "subtitle": "Direction Générale des Transports Terrestres - République du Bénin",
        "edition": "Édition 2011",
        "total_questions": len(raw_questions),
        "total_chapters": 11,
        "official_pass_score": 14,
        "official_max_score": 20,
        "default_series_size": 20
    },
    "course_ch1": course_sections,
    "chapters": chapters_output
}

json_path = os.path.join(output_data_dir, "qcm_data.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(full_data, f, ensure_ascii=False, indent=2)

js_path = os.path.join(output_data_dir, "qcm_data.js")
with open(js_path, "w", encoding="utf-8") as f:
    f.write("window.QCM_DATA = " + json.dumps(full_data, ensure_ascii=False) + ";\n")

print(f"Extraction completed successfully! Saved to {json_path} and {js_path}.")

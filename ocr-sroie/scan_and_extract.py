import json
from PIL import Image
import pytesseract
import torch
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
import os
import glob

LABEL_LIST = ['O', 'ADDRESS', 'COMPANY', 'DATE', 'TOTAL']  # must match your training
ID2LABEL = {i: l for i, l in enumerate(LABEL_LIST)}

def ocr_tesseract(image_path):
    img = Image.open(image_path).convert("RGB")
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    words, boxes = [], []
    for i, w in enumerate(data['text']):
        if not w or not w.strip():
            continue
        x, y, wdt, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
        words.append(w)
        boxes.append([x, y, x + wdt, y + h])
    return img, words, boxes

def normalize_boxes(boxes, width, height):
    norm = []
    for (x0, y0, x1, y1) in boxes:
        nx0 = int(round(max(0, min(1000, x0 / width * 1000))))
        ny0 = int(round(max(0, min(1000, y0 / height * 1000))))
        nx1 = int(round(max(0, min(1000, x1 / width * 1000))))
        ny1 = int(round(max(0, min(1000, y1 / height * 1000))))
        norm.append([nx0, ny0, nx1, ny1])
    return norm

def predict_image(image_path, model, processor, device='cpu'):
    img, words, boxes = ocr_tesseract(image_path)
    w, h = img.size
    norm_boxes = normalize_boxes(boxes, w, h)
    encoding = processor(images=img, text=words,
                         boxes=norm_boxes,
                         truncation=True, padding='max_length', max_length=512, return_tensors='pt')
    for k, v in encoding.items():
        encoding[k] = v.to(device)
    with torch.no_grad():
        outputs = model(**encoding)
        preds = outputs.logits.argmax(-1).squeeze().tolist()
    word_ids = encoding.word_ids(batch_index=0)  # map tokens -> word index (None for special tokens)
    word_labels = {}
    for tok_idx, word_id in enumerate(word_ids):
        if word_id is None:
            continue
        if word_id not in word_labels:
            word_labels[word_id] = ID2LABEL[preds[tok_idx]]
    # Build entities by grouping consecutive words with same non-O label
    entities = []
    cur = None
    for i, wtext in enumerate(words):
        lbl = word_labels.get(i, 'O')
        if lbl == 'O':
            if cur:
                entities.append(cur); cur = None
            continue
        bbox = boxes[i]
        if cur is None or cur['label'] != lbl:
            if cur:
                entities.append(cur)
            cur = {'label': lbl, 'text': wtext, 'boxes': [bbox]}
        else:
            cur['text'] += ' ' + wtext
            cur['boxes'].append(bbox)
    if cur:
        entities.append(cur)

    # Post-processing: merge nearby COMPANY fragments and sanitize entities
    def box_center_y(b):
        return (b[1] + b[3]) / 2

    # merge COMPANY fragments that are close vertically
    companies = [e for e in entities if e['label'] == 'COMPANY']
    others = [e for e in entities if e['label'] != 'COMPANY']
    merged_comp = []
    if companies:
        # sort by y-center
        companies.sort(key=lambda e: min(box_center_y(b) for b in e['boxes']))
        cur = companies[0].copy()
        for e in companies[1:]:
            ycur = min(box_center_y(b) for b in cur['boxes'])
            ye = min(box_center_y(b) for b in e['boxes'])
            if abs(ye - ycur) <= 40:  # threshold in pixels
                # merge
                cur['text'] = (cur['text'] + ' ' + e['text']).strip()
                cur['boxes'].extend(e['boxes'])
            else:
                merged_comp.append(cur)
                cur = e.copy()
        merged_comp.append(cur)

    # sanitize: remove tiny non-informative labels and clean DATE text
    import re
    date_re = re.compile(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})")
    clean_entities = []
    # add merged companies first
    # helper to apply fuzzy fixes to company text
    def fix_company_text(txt: str) -> str:
        s = txt.strip()
        # common OCR errors -> corrections
        s = re.sub(r"8HD", "BHD", s, flags=re.IGNORECASE)
        s = re.sub(r"\bBDH\b", "BHD", s, flags=re.IGNORECASE)
        s = re.sub(r"SDN\s*BND", "SDN BHD", s, flags=re.IGNORECASE)
        s = re.sub(r"\b0JC\b", "OJC", s, flags=re.IGNORECASE)
        # remove stray punctuation
        s = s.replace(')', '').replace('(', '').strip()
        return s

    for e in merged_comp:
        txt = fix_company_text(e['text'])
        # drop very short garbage
        if len(re.sub(r"\W+", "", txt)) < 2:
            continue
        clean_entities.append({'label': 'COMPANY', 'text': txt, 'boxes': e['boxes']})

    # process other entities
    for e in others:
        txt = e['text'].strip()
        if e['label'] == 'DATE':
            m = date_re.search(txt)
            if m:
                txt = m.group(1)
            else:
                # drop single-char/garbage dates
                if len(re.sub(r"\D+", "", txt)) < 4:
                    continue
        if e['label'] == 'TOTAL':
            # extract monetary amount like 123.45
            m = re.search(r"(\d+[.,]\d{2})", txt)
            if m:
                txt = m.group(1).replace(',', '.')
            else:
                # fallback: strip non-digit/dot characters
                txt = re.sub(r"[^0-9.]", "", txt)
                if not txt:
                    continue
        # drop tiny garbage company/date fragments
        if e['label'] in ('COMPANY', 'DATE') and len(re.sub(r"\W+", "", txt)) < 2:
            continue
        clean_entities.append({'label': e['label'], 'text': txt, 'boxes': e['boxes']})

    # If company list is empty or looks like garbage, try header fallback:
    if not any(e['label'] == 'COMPANY' for e in clean_entities):
        try:
            page_top_thr = h * 0.25
            header_words = []
            for idx, (wtext, bbox) in enumerate(zip(words, boxes)):
                cy = box_center_y(bbox)
                if cy <= page_top_thr:
                    header_words.append((idx, wtext, bbox))
            # join header words ordered by x-coordinate and look for company markers
            if header_words:
                header_words.sort(key=lambda t: t[2][0])
                joined = ' '.join(t[1] for t in header_words)
                if re.search(r"\b(SDN|BHD|MARKETING|BOOK|TRADING|INDUSTRIAL)\b", joined, flags=re.IGNORECASE):
                    cand = fix_company_text(joined)
                    header_boxes = [t[2] for t in header_words]
                    clean_entities.insert(0, {'label': 'COMPANY', 'text': cand, 'boxes': header_boxes})
        except Exception:
            pass

    # Merge nearby entities of same label and remove tiny garbage entries
    def entity_y_range(e):
        ys = [b[1] for b in e['boxes']] + [b[3] for b in e['boxes']]
        return min(ys), max(ys)

    def horiz_overlap(a, b):
        # approximate overlap between two boxes lists using x ranges
        ax = [min(bb[0] for bb in a), max(bb[2] for bb in a)]
        bx = [min(bb[0] for bb in b), max(bb[2] for bb in b)]
        return max(0, min(ax[1], bx[1]) - max(ax[0], bx[0]))

    final_entities = []
    for label in ('COMPANY', 'ADDRESS', 'DATE', 'TOTAL'):
        ents = [e for e in clean_entities if e['label'] == label]
        if not ents:
            continue
        # drop very small/address garbage (single digits, stray chars)
        filtered = []
        for e in ents:
            txt_clean = re.sub(r"\W+", "", e['text'])
            if label == 'ADDRESS' and len(txt_clean) < 2:
                continue
            filtered.append(e)
        if not filtered:
            continue
        # sort by top y then left x
        def ent_key(e):
            top = min(b[1] for b in e['boxes'])
            left = min(b[0] for b in e['boxes'])
            return (top, left)
        filtered.sort(key=ent_key)

        # merge nearby entries: if vertical ranges overlap/near and horizontal overlap small, merge texts
        merged = []
        cur = filtered[0].copy()
        for e in filtered[1:]:
            cur_top, cur_bot = entity_y_range(cur)
            e_top, e_bot = entity_y_range(e)
            vdist = max(0, max(e_top - cur_bot, cur_top - e_bot))
            h_ov = horiz_overlap(cur['boxes'], e['boxes'])
            if vdist <= 20 or h_ov > 0:
                # merge
                cur['text'] = (cur['text'] + ' ' + e['text']).strip()
                cur['boxes'].extend(e['boxes'])
            else:
                merged.append(cur)
                cur = e.copy()
        merged.append(cur)

        # If after merging there are multiple entries, prefer the longest text
        merged.sort(key=lambda x: len(re.sub(r"\W+", "", x['text'])), reverse=True)
        best = merged[0]
        final_entities.append(best)

    return {'image': image_path, 'entities': final_entities}

if __name__ == '__main__':
    DEVICE = 'cpu'
    # Try to load a local saved model/processor first. Use local_files_only to avoid HF Hub lookups.
    processor = None
    model = None
    # make paths relative to this script (ocr-sroie folder)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    final_dir = os.path.join(BASE_DIR, 'layoutlmv3-sroie2019-final-faster')
    ckpt_root = os.path.join(BASE_DIR, 'layoutlmv3-sroie2019-faster')
    try:
        processor = LayoutLMv3Processor.from_pretrained(final_dir, local_files_only=True)
    except Exception:
        print("fallback")
        # fallback to base processor from hub (no OCR)
        processor = LayoutLMv3Processor.from_pretrained('microsoft/layoutlmv3-base', apply_ocr=False)
    try:
        model = LayoutLMv3ForTokenClassification.from_pretrained(final_dir, local_files_only=True)
    except Exception:
        print("nasa checkpt")
        # try to pick the latest checkpoint under the training output folder
        ckpts = sorted(glob.glob(os.path.join(ckpt_root, 'checkpoint-*')), key=lambda p: int(p.split('-')[-1]) if p.split('-')[-1].isdigit() else -1)
        if ckpts:
            latest = ckpts[-1]
            model = LayoutLMv3ForTokenClassification.from_pretrained(latest, local_files_only=True)
            # try to load processor from checkpoint if saved there
            try:
                processor = LayoutLMv3Processor.from_pretrained(latest, local_files_only=True)
            except Exception:
                pass
        else:
            raise
    model.to(DEVICE).eval() # type: ignore

    imgs = [
            '../data/SROIE2019/train/img/X00016469612.jpg', 
            '../data/SROIE2019/test/img/X00016469670.jpg', 
            '../data/SROIE2019/test/img/X51005230605.jpg'
        ] 

    # # collect test images from repo test/img (compact)
    # imgs = glob.glob(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'data', 'SROIE2019', 'test', 'img', '*.jpg'))
    
    results = [predict_image(p, model, processor, device=DEVICE) for p in imgs]
    print(json.dumps(results, indent=2, ensure_ascii=False))
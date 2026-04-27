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
    return {'image': image_path, 'entities': entities}

if __name__ == '__main__':
    DEVICE = 'cpu'
    # Try to load a local saved model/processor first. Use local_files_only to avoid HF Hub lookups.
    processor = None
    model = None
    # make paths relative to this script (ocr-sroie folder)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    final_dir = os.path.join(BASE_DIR, 'layoutlmv3-sroie2019-final')
    ckpt_root = os.path.join(BASE_DIR, 'layoutlmv3-sroie2019')
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

    imgs = ['../data/SROIE2019/test/img/X00016469670.jpg'] 

    # # collect test images from repo test/img (compact)
    # imgs = glob.glob(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'data', 'SROIE2019', 'test', 'img', '*.jpg'))
    
    results = [predict_image(p, model, processor, device=DEVICE) for p in imgs]
    print(json.dumps(results, indent=2, ensure_ascii=False))
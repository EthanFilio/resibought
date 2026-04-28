import json
from PIL import Image
import pytesseract
import torch
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
import os
import glob
import re


def normalize_boxes(boxes, width, height):
    norm = []
    for x0, y0, x1, y1 in boxes:
        nx0 = int(round(max(0, min(1000, x0 / width * 1000))))
        ny0 = int(round(max(0, min(1000, y0 / height * 1000))))
        nx1 = int(round(max(0, min(1000, x1 / width * 1000))))
        ny1 = int(round(max(0, min(1000, y1 / height * 1000))))
        norm.append([nx0, ny0, nx1, ny1])
    return norm

def ocr_tesseract(image_path, psm=3):
    """
    Tesseract OCR with configurable PSM (Page Segmentation Mode):
    0=OSD only, 1=auto+OSD, 2=auto, 3=auto (default), 4=single col of var sizes,
    5=uniform block, 6=single uniform block, 7=single text line, 8=single word,
    9=circle word, 10=char, 11=sparse text, 12=sparse text+OSD, 13=auto+sparse
    """
    img = Image.open(image_path).convert("RGB")
    custom_config = f'--psm {psm}'
    data = pytesseract.image_to_data(img, config=custom_config, output_type=pytesseract.Output.DICT)
    
    words, boxes, line_keys = [], [], []
    for i, w in enumerate(data['text']):
        if not w or not w.strip():
            continue
        try:
            conf = float(data['conf'][i])
        except Exception:
            conf = -1.0
        if conf >= 0 and conf < 25:
            continue
        x, y, wdt, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
        words.append(w)
        boxes.append([x, y, x + wdt, y + h])
        line_keys.append((data['block_num'][i], data['par_num'][i], data['line_num'][i]))
    return img, words, boxes, line_keys


def looks_like_total_line(line_words):
    labels = [word['label'] for word in line_words]
    texts = [word['text'].lower() for word in line_words]
    has_item_labels = any(label in ('count', 'item') for label in labels)
    has_total_label = any(label == 'total' for label in labels)
    has_total_keyword = any(token in ('total', 'grand', 'balance', 'due', 'subtotal', 'sub') for token in texts)
    return (has_total_label or has_total_keyword) and not has_item_labels


def clean_money_text(txt):
    """
    Extract and clean monetary amount from text using regex.
    Examples: "123.45", "123,456", "100,000 VND" -> "123.45" or "100,000"
    """
    if not txt:
        return ''
    
    txt = txt.strip()
    
    # Pattern 1: Try to extract standard monetary format XXX,XXX.XX or XXX.XXX,XX
    m = re.search(r'(\d{1,3}[.,]\d{3}(?:[.,]\d{2,3})?)', txt)
    if m:
        return m.group(1)
    
    # Pattern 2: Try simple number with decimals
    m = re.search(r'(\d+[.,]\d+)', txt)
    if m:
        return m.group(1)
    
    # Pattern 3: Just extract all digits and reconstruct
    m = re.search(r'(\d+)', txt)
    if m:
        return m.group(1)
    
    return txt


def is_money_token(token):
    stripped = token.replace(',', '').replace('.', '').replace('$', '').replace(' ', '')
    return stripped.isdigit() and any(char.isdigit() for char in token)


def clean_join(tokens):
    return ' '.join(token for token in tokens if token).strip()


def pick_price_text(line_words):
    money_words = [word for word in line_words if is_money_token(word['text'])]
    if not money_words:
        return ''

    money_words = sorted(money_words, key=lambda item: item['box'][0])
    return clean_join([word['text'] for word in money_words[-2:]])


def pick_largest_price_text(line_words):
    """Extract largest monetary amount from line words using regex patterns."""
    money_words = [word for word in line_words if is_money_token(word['text'])]
    if not money_words:
        return ''

    # First try to extract amounts with decimal/comma patterns: 123.45 or 123,45 or 123,456
    candidates = []
    for word in money_words:
        text = word['text']
        # Pattern 1: XXX,XXX or XXX.XXX format (thousands separator)
        m = re.search(r'(\d{1,3}[.,]\d{3}(?:[.,]\d{2,3})*)', text)
        if m:
            candidates.append((m.group(1), text))
            continue
        # Pattern 2: just numbers
        m = re.search(r'(\d+)', text)
        if m:
            candidates.append((m.group(1), text))
    
    if not candidates:
        return ''
    
    # Convert all to numeric for comparison (remove separators)
    def numeric_value(s):
        cleaned = s.replace(',', '').replace('.', '')
        try:
            return int(cleaned)
        except ValueError:
            return 0
    
    best = max(candidates, key=lambda c: numeric_value(c[0]))
    return best[1]  # Return original format


def group_words_into_lines(words, boxes, labels, line_keys):
    line_items = []
    current_key = None
    current_line = None

    for word_text, bbox, label, line_key in sorted(
        zip(words, boxes, labels, line_keys),
        key=lambda item: (item[3], item[1][0]),
    ):
        if line_key != current_key:
            current_key = line_key
            current_line = {
                'words': [],
            }
            line_items.append(current_line)

        current_line['words'].append({
            'text': word_text,
            'box': bbox,
            'label': label,
        })

    rows = []
    for index, line in enumerate(line_items):
        line_words = sorted(line['words'], key=lambda item: item['box'][0])
        label_text = {'count': [], 'item': [], 'price': [], 'total': []}
        label_boxes = {'count': [], 'item': [], 'price': [], 'total': []}

        for word in line_words:
            label = word['label']
            if label in label_text:
                label_text[label].append(word['text'])
                label_boxes[label].append(word['box'])

        count_text = clean_join(label_text['count'])
        item_text = clean_join(label_text['item'])
        price_text = clean_join(label_text['price']) or pick_price_text(line_words)
        total_text = clean_join(label_text['total']) or pick_largest_price_text(line_words)

        row = {
            'count': count_text,
            'item': item_text,
            'price': price_text,
        }

        is_last_line = index == len(line_items) - 1
        if looks_like_total_line(line_words) and (is_last_line or any(word['label'] == 'total' for word in line_words)):
            row['line_type'] = 'total'
            row['text'] = total_text or clean_join([word['text'] for word in line_words])
            row['boxes'] = [word['box'] for word in line_words]
        else:
            row['line_type'] = 'item'
            row['boxes'] = {
                'count': label_boxes['count'],
                'item': label_boxes['item'],
                'price': label_boxes['price'],
            }

        if (
            row['line_type'] == 'item'
            and not row['count']
            and not row['item']
            and row['price']
            and rows
            and rows[-1]['line_type'] == 'item'
            and not rows[-1]['price']
        ):
            rows[-1]['price'] = row['price']
            rows[-1]['boxes']['price'] = row['boxes']['price']
            continue

        if row['count'] or row['item'] or row['price'] or row.get('text'):
            rows.append(row)

    if not any(row['line_type'] == 'total' for row in rows):
        all_prices = []
        for row in rows:
            if row.get('price'):
                all_prices.append(row['price'])
        if all_prices:
            def extract_numeric(s):
                cleaned = s.replace(',', '').replace('.', '').replace('$', '').replace(' ', '')
                try:
                    return int(cleaned)
                except ValueError:
                    return 0
            largest = max(all_prices, key=extract_numeric)
            rows.append({
                'count': '',
                'item': '',
                'price': largest,
                'line_type': 'total',
                'text': largest,
                'boxes': [],
            })

    # Clean up all price fields using regex-based extraction
    for row in rows:
        if row.get('price'):
            row['price'] = clean_money_text(row['price'])

    return rows


def predict_image(image_path, model, processor, id2label, device='cpu', psm=3):
    img, words, boxes, line_keys = ocr_tesseract(image_path, psm=psm)
    width, height = img.size
    norm_boxes = normalize_boxes(boxes, width, height)

    encoding = processor(
        images=img,
        text=words,
        boxes=norm_boxes,
        truncation=True,
        padding='max_length',
        max_length=512,
        return_tensors='pt',
    )
    for key, value in encoding.items():
        encoding[key] = value.to(device)

    with torch.no_grad():
        outputs = model(**encoding)
        preds = outputs.logits.argmax(-1).squeeze().tolist()

    word_ids = encoding.word_ids(batch_index=0)
    word_labels = ['O'] * len(words)
    for token_idx, word_id in enumerate(word_ids):
        if word_id is None:
            continue
        if word_labels[word_id] == 'O':
            label_id = int(preds[token_idx])
            word_labels[word_id] = id2label.get(label_id, 'O')

    grouped_rows = group_words_into_lines(words, boxes, word_labels, line_keys)

    return {'image': image_path, 'rows': grouped_rows}


if __name__ == '__main__':
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    base_dir = os.path.abspath(os.path.dirname(__file__))
    checkpoint_dir = os.path.abspath(os.path.join(base_dir, '..', 'layoutlmv3-cord-model', 'checkpoint-400'))

    try:
        processor = LayoutLMv3Processor.from_pretrained(checkpoint_dir, local_files_only=True)
    except Exception:
        processor = LayoutLMv3Processor.from_pretrained('microsoft/layoutlmv3-base', apply_ocr=False)

    model = LayoutLMv3ForTokenClassification.from_pretrained(checkpoint_dir, local_files_only=True)
    model.to(device).eval()

    id2label = {int(key): value for key, value in model.config.id2label.items()}

    cord_test_image_dir = os.path.abspath(os.path.join(base_dir, '..', 'data', 'CORD_1000', 'test', 'image'))

    # Use one image first while validating the output JSON.
    test_image = os.path.join(cord_test_image_dir, 'receipt_00028.png')
    imgs = [test_image] if os.path.exists(test_image) else []

    # Uncomment this after the single-image test looks correct.
    # imgs = sorted(glob.glob(os.path.join(cord_test_image_dir, '*.png')))

    results = [predict_image(path, model, processor, id2label, device=device) for path in imgs]

    print(json.dumps(results, indent=2, ensure_ascii=False))


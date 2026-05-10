import json
import os
import glob
import re
from typing import Any, List, Tuple

from PIL import Image
import torch
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification

# PaddleOCR (external dependency)
try:
	# For Windows CPU compatibility: disable MKLDNN before importing Paddle/PaddleOCR
	# This must be set before Paddle is imported to avoid oneDNN runtime errors.
	os.environ.setdefault('FLAGS_use_mkldnn', '0')
	from paddleocr import PaddleOCR
except Exception as e:
	raise ImportError("paddleocr is required. Install with 'pip install paddleocr paddlepaddle' (follow PaddlePaddle install docs for GPU).")

# Import canonical CORD label list and id2label mapping
from cord1000_val_loader import LABEL_LIST as CORD_LABEL_LIST, id2label as CORD_ID2LABEL

# Normalize to expected mapping name
ID2LABEL = {int(k): v for k, v in CORD_ID2LABEL.items()}

# Initialize PaddleOCR once
OCR = PaddleOCR(
	use_textline_orientation=True,
	lang='en',
	use_gpu=False,
	enable_mkldnn=False,
)


def ocr_paddle(image_path: str) -> Tuple[Image.Image, List[str], List[List[int]]]:
	img = Image.open(image_path).convert("RGB")
	# PaddleOCR output shape varies by version (nested list, dict, batch wrapper).
	res = OCR.ocr(image_path)
	words = []
	boxes = []

	def _coord_to_float(v: Any) -> float:
		# unwrap nested sequences or numpy scalars to a Python float
		try:
			if hasattr(v, 'item'):
				return float(v.item())
		except Exception:
			pass
		if isinstance(v, (list, tuple)):
			if len(v) == 0:
				return 0.0
			return _coord_to_float(v[0])
		return float(v)

	def _is_point(p: Any) -> bool:
		if not isinstance(p, (list, tuple)) or len(p) < 2:
			return False
		try:
			_coord_to_float(p[0])
			_coord_to_float(p[1])
			return True
		except Exception:
			return False

	def _is_polygon(poly: Any) -> bool:
		if not isinstance(poly, (list, tuple)) or len(poly) < 4:
			return False
		return all(_is_point(pt) for pt in poly)

	def _extract_pairs(obj: Any) -> List[Tuple[List[Any], str]]:
		pairs: List[Tuple[List[Any], str]] = []
		if isinstance(obj, dict):
			# Some versions return dict-style payloads
			if 'rec_texts' in obj and 'rec_polys' in obj:
				for poly, txt in zip(obj.get('rec_polys', []), obj.get('rec_texts', [])):
					if _is_polygon(poly):
						pairs.append((poly, str(txt)))
				return pairs
			if ('text' in obj or 'rec_text' in obj) and ('poly' in obj or 'rec_poly' in obj or 'dt_poly' in obj):
				poly = obj.get('poly', obj.get('rec_poly', obj.get('dt_poly')))
				txt = obj.get('text', obj.get('rec_text', ''))
				if _is_polygon(poly):
					pairs.append((poly, str(txt)))
				return pairs
			for v in obj.values():
				pairs.extend(_extract_pairs(v))
			return pairs

		if isinstance(obj, (list, tuple)):
			# Canonical detection tuple: [poly, (text, score)]
			if len(obj) >= 2 and _is_polygon(obj[0]):
				txt_obj = obj[1]
				txt = txt_obj[0] if isinstance(txt_obj, (list, tuple)) and len(txt_obj) > 0 else txt_obj
				pairs.append((obj[0], str(txt)))
				return pairs
			for it in obj:
				pairs.extend(_extract_pairs(it))
		return pairs

	for box_pts, text in _extract_pairs(res):
		xs = [int(round(_coord_to_float(p[0]))) for p in box_pts]
		ys = [int(round(_coord_to_float(p[1]))) for p in box_pts]
		x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
		# split text into words so tokenization aligns better with training words
		toks = text.split()
		if len(toks) <= 1:
			words.append(text)
			boxes.append([x0, y0, x1, y1])
		else:
			# approximate splitting by assigning equal-width sub-boxes
			width = x1 - x0
			if width <= 0:
				# fallback: add whole
				words.append(text)
				boxes.append([x0, y0, x1, y1])
			else:
				sub_w = max(1, width // len(toks))
				for i, t in enumerate(toks):
					sx = x0 + i * sub_w
					ex = sx + sub_w if i < len(toks) - 1 else x1
					words.append(t)
					boxes.append([sx, y0, ex, y1])
	return img, words, boxes


def normalize_boxes(boxes: List[List[int]], width: int, height: int) -> List[List[int]]:
	norm = []
	for (x0, y0, x1, y1) in boxes:
		nx0 = int(round(max(0, min(1000, x0 / width * 1000))))
		ny0 = int(round(max(0, min(1000, y0 / height * 1000))))
		nx1 = int(round(max(0, min(1000, x1 / width * 1000))))
		ny1 = int(round(max(0, min(1000, y1 / height * 1000))))
		norm.append([nx0, ny0, nx1, ny1])
	return norm


def predict_image(image_path: str, model, processor, device: str = 'cpu') -> dict:
	img, words, boxes = ocr_paddle(image_path)
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
	word_ids = encoding.word_ids(batch_index=0)
	word_labels = {}
	for tok_idx, word_id in enumerate(word_ids):
		if word_id is None:
			continue
		if word_id not in word_labels:
			lbl_id = preds[tok_idx]
			word_labels[word_id] = ID2LABEL.get(lbl_id, 'O')

	# Group consecutive words by label
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

	# Post-processing specific to CORD label types
	clean_entities = []
	money_re = re.compile(r"(\d+[.,]\d{2})")
	for e in entities:
		txt = e['text'].strip()
		if e['label'] in ('ITEM_PRICE', 'ITEM_UNITPRICE', 'ITEM_DISCOUNT', 'TOTAL'):
			m = money_re.search(txt)
			if m:
				txt = m.group(1).replace(',', '.')
			else:
				txt = re.sub(r"[^0-9.]", "", txt)
				if not txt:
					continue
		if e['label'] == 'ITEM_QTY':
			# try to extract numeric qty
			q = re.sub(r"[^0-9.]", "", txt)
			if not q:
				continue
			txt = q
		# drop tiny garbage
		if len(re.sub(r"\W+", "", txt)) < 1:
			continue
		clean_entities.append({'label': e['label'], 'text': txt, 'boxes': e['boxes']})

	def _entity_center_y(ent: dict) -> float:
		ys = [b[1] for b in ent['boxes']] + [b[3] for b in ent['boxes']]
		return (min(ys) + max(ys)) / 2.0

	def _entity_right_x(ent: dict) -> int:
		return max(b[2] for b in ent['boxes'])

	# If ITEM_VARIANT appears as a standalone row (no nearby ITEM_NAME), treat it as ITEM_NAME.
	name_rows = [e for e in clean_entities if e['label'] == 'ITEM_NAME']
	for e in clean_entities:
		if e['label'] != 'ITEM_VARIANT':
			continue
		cy = _entity_center_y(e)
		if not any(abs(cy - _entity_center_y(n)) <= 20 for n in name_rows):
			e['label'] = 'ITEM_NAME'
			name_rows.append(e)

	# Recover missing ITEM_PRICE on rows that look like item rows.
	price_rows = [e for e in clean_entities if e['label'] in ('ITEM_PRICE', 'ITEM_UNITPRICE')]
	for item in [e for e in clean_entities if e['label'] == 'ITEM_NAME']:
		item_cy = _entity_center_y(item)
		item_rx = _entity_right_x(item)
		if any(abs(item_cy - _entity_center_y(p)) <= 24 for p in price_rows):
			continue

		best = None
		for wtext, bb in zip(words, boxes):
			cy = (bb[1] + bb[3]) / 2.0
			if abs(cy - item_cy) > 24:
				continue
			if bb[0] < item_rx - 10:
				continue
			raw = re.sub(r"[^0-9.,]", "", wtext)
			digits = re.sub(r"\D+", "", raw)
			if len(digits) < 3:
				continue
			score = (len(digits), bb[2])
			if best is None or score > best[0]:
				best = (score, raw, bb)

		if best is not None:
			raw_val = best[1].replace(',', '.')
			clean_entities.append({'label': 'ITEM_PRICE', 'text': raw_val, 'boxes': [best[2]]})
			price_rows.append(clean_entities[-1])

	# Prefer one entry per label: for items we keep all, for TOTAL prefer longest/last
	final_entities = []
	# keep all ITEM_* entries
	for e in clean_entities:
		if e['label'].startswith('ITEM_'):
			final_entities.append(e)
	# find TOTAL if present
	totals = [e for e in clean_entities if e['label'] == 'TOTAL']
	if totals:
		# pick one with longest numeric content
		totals.sort(key=lambda x: len(re.sub(r"\D+", "", x['text'])), reverse=True)
		final_entities.append(totals[0])

	return {'image': image_path, 'entities': final_entities}


if __name__ == '__main__':
	device = 'cuda' if torch.cuda.is_available() else 'cpu'
	BASE_DIR = os.path.abspath(os.path.dirname(__file__))
	final_dir = os.path.join(BASE_DIR, 'layoutlmv3-cord1000-final')
	ckpt_root = os.path.join(BASE_DIR, 'layoutlmv3-cord1000')

	# Load processor and model, prefer final_dir, else pick latest numeric checkpoint
	try:
		processor = LayoutLMv3Processor.from_pretrained(final_dir, local_files_only=True)
	except Exception:
		processor = LayoutLMv3Processor.from_pretrained('microsoft/layoutlmv3-base', apply_ocr=False)

	model = None
	try:
		model = LayoutLMv3ForTokenClassification.from_pretrained(final_dir, local_files_only=True)
	except Exception:
		ckpts = sorted(glob.glob(os.path.join(ckpt_root, 'checkpoint-*')),
					   key=lambda p: int(p.split('-')[-1]) if p.split('-')[-1].isdigit() else -1)
		if ckpts:
			latest = ckpts[-1]
			model = LayoutLMv3ForTokenClassification.from_pretrained(latest, local_files_only=True)
			try:
				processor = LayoutLMv3Processor.from_pretrained(latest, local_files_only=True)
			except Exception:
				pass
		else:
			raise RuntimeError('No local CORD model found under expected directories.')

	model.to(device).eval()

	# Collect sample images from data/CORD_1000/dev/image
	sample_dir = os.path.join(os.path.abspath(os.path.join(BASE_DIR, '..')), 'data', 'CORD_1000', 'dev', 'image')
	imgs = glob.glob(os.path.join(sample_dir, '*'))[:5]
	if not imgs:
		print('No sample images found in data/CORD_1000/dev/image. Please provide paths.')
	else:
		imgs = [
			'../data/CORD_1000/test/image/receipt_00080.png',
        ]
		results = [predict_image(p, model, processor, device=device) for p in imgs]
		print(json.dumps(results, indent=2, ensure_ascii=False))

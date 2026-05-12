import json
import os
import glob
import re
import time
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
	raise ImportError("`paddleocr is required. Install with 'pip install paddleocr paddlepaddle' (follow PaddlePaddle install docs for GPU).")

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


def _softmax(logits: List[float]) -> List[float]:
	max_l = max(logits)
	exps = [2.718281828 ** (x - max_l) for x in logits]
	s = sum(exps)
	return [x / s for x in exps]


class RobustItemClassifier:
	"""
	Multi-signal classifier that re-evaluates whether each entity labeled
	ITEM_NAME or ITEM_VARIANT is correctly assigned.

	Signals used (weighted sum → variant_score in [0, 1]):
	  model_confidence  – softmax P(ITEM_VARIANT) from the token classifier
	  has_parent_name   – an ITEM_NAME exists directly above within proximity
	  indentation       – entity is indented further right than peer item names
	  no_row_price      – no price/qty entity shares the same row (prices alongside names are normal; variants rarely have them)
	  text_keywords     – modifier words (add, extra, large, no, with …)
	  text_prefix       – starts with +, -, *, bullet, or parenthesis
	  text_casing       – lowercase or mixed case (receipts use ALL-CAPS for names)
	"""

	VARIANT_KEYWORDS = frozenset({
		'add', 'extra', 'no', 'with', 'without', 'upsize', 'downsize',
		'upgrade', 'large', 'medium', 'small', 'regular', 'hot', 'iced',
		'ice', 'sugar', 'free', 'double', 'single', 'half', 'choice',
		'option', 'style', 'flavor', 'topping', 'sauce', 'side',
		'dressing', 'combo', 'size', 'type', 'addon', 'add-on',
	})

	VARIANT_PREFIX_CHARS = frozenset('+−-*·•>(')

	# Signal weights (must be kept in sync with _SIGNAL_KEYS below)
	_WEIGHTS = {
		'model_confidence': 0.38,
		'has_parent_name':  0.22,
		'indentation':      0.15,
		'no_row_price':     0.10,
		'text_keywords':    0.08,
		'text_prefix':      0.04,
		'text_casing':      0.03,
	}

	# Score ≥ threshold → ITEM_VARIANT
	VARIANT_THRESHOLD = 0.42

	def __init__(
		self,
		vertical_proximity_px: int = 65,
		row_proximity_px: int = 24,
		indentation_tolerance_px: int = 15,
	):
		self.vertical_proximity_px = vertical_proximity_px
		self.row_proximity_px = row_proximity_px
		self.indentation_tolerance_px = indentation_tolerance_px

	# ------------------------------------------------------------------ helpers

	@staticmethod
	def _bbox(ent: dict) -> List[int]:
		xs0 = [b[0] for b in ent['boxes']]
		ys0 = [b[1] for b in ent['boxes']]
		xs1 = [b[2] for b in ent['boxes']]
		ys1 = [b[3] for b in ent['boxes']]
		return [min(xs0), min(ys0), max(xs1), max(ys1)]

	def _cy(self, ent: dict) -> float:
		bb = self._bbox(ent)
		return (bb[1] + bb[3]) / 2.0

	def _lx(self, ent: dict) -> int:
		return min(b[0] for b in ent['boxes'])

	# ----------------------------------------------------------------- signals

	def _sig_model_confidence(self, ent: dict) -> float:
		conf = ent.get('confidence', {})
		p_name = conf.get('ITEM_NAME', 0.0)
		p_var  = conf.get('ITEM_VARIANT', 0.0)
		denom  = p_name + p_var
		if denom == 0:
			# Fall back to label: treat model label as a weak 0.65 prior
			return 0.65 if ent['label'] == 'ITEM_VARIANT' else 0.35
		return p_var / denom

	def _sig_has_parent_name(self, ent: dict, name_ents: List[dict]) -> float:
		"""1.0 if an ITEM_NAME sits directly above within vertical_proximity_px."""
		cy = self._cy(ent)
		for n in name_ents:
			if n is ent:
				continue
			n_cy = self._cy(n)
			# Name must be above (lower y value) and within window
			if 0 < (cy - n_cy) <= self.vertical_proximity_px:
				return 1.0
		return 0.0

	def _sig_indentation(self, ent: dict, name_ents: List[dict]) -> float:
		"""How much further right this entity starts vs. the median of item names."""
		peer_lefts = [self._lx(n) for n in name_ents if n is not ent]
		if not peer_lefts:
			return 0.0
		median_left = sorted(peer_lefts)[len(peer_lefts) // 2]
		delta = self._lx(ent) - median_left - self.indentation_tolerance_px
		if delta <= 0:
			return 0.0
		return min(1.0, delta / 35.0)  # 35 px of extra indent → full score

	def _sig_no_row_price(self, ent: dict, price_ents: List[dict]) -> float:
		"""
		Returns 0.0 when a price/qty entity is on the same row (name-like),
		0.6 when nothing is alongside (mildly variant-like — variants sometimes
		carry their own price, so we cap at 0.6, not 1.0).
		"""
		cy = self._cy(ent)
		for p in price_ents:
			if abs(cy - self._cy(p)) <= self.row_proximity_px:
				return 0.0
		return 0.6

	def _sig_text_keywords(self, text: str) -> float:
		words = set(re.sub(r"[^a-z\s]", "", text.lower()).split())
		hits = words & self.VARIANT_KEYWORDS
		return min(1.0, len(hits) / 1.5)  # 2 hits → full score

	def _sig_text_prefix(self, text: str) -> float:
		s = text.lstrip()
		return 1.0 if (s and s[0] in self.VARIANT_PREFIX_CHARS) else 0.0

	def _sig_text_casing(self, text: str) -> float:
		alpha = re.sub(r"[^a-zA-Z]", "", text)
		if not alpha:
			return 0.0
		if alpha == alpha.upper():
			return 0.0   # ALL CAPS → name-like
		if alpha == alpha.lower():
			return 0.85  # all lowercase → variant-like
		return 0.25      # mixed case → weak variant lean

	# ----------------------------------------------------------------- classify

	def classify(self, entities: List[dict]) -> List[dict]:
		"""
		Re-label ITEM_NAME / ITEM_VARIANT entities in-place using multi-signal
		scoring.  Processes entities in document order so decisions made earlier
		(e.g. promoting a standalone variant to a name) inform later ones.
		"""
		name_ents  = [e for e in entities if e['label'] == 'ITEM_NAME']
		price_ents = [e for e in entities if e['label'] in ('ITEM_PRICE', 'ITEM_UNITPRICE', 'ITEM_QTY')]

		for ent in entities:
			if ent['label'] not in ('ITEM_NAME', 'ITEM_VARIANT'):
				continue

			scores = {
				'model_confidence': self._sig_model_confidence(ent),
				'has_parent_name':  self._sig_has_parent_name(ent, name_ents),
				'indentation':      self._sig_indentation(ent, name_ents),
				'no_row_price':     self._sig_no_row_price(ent, price_ents),
				'text_keywords':    self._sig_text_keywords(ent['text']),
				'text_prefix':      self._sig_text_prefix(ent['text']),
				'text_casing':      self._sig_text_casing(ent['text']),
			}

			variant_score = sum(self._WEIGHTS[k] * v for k, v in scores.items())
			new_label = 'ITEM_VARIANT' if variant_score >= self.VARIANT_THRESHOLD else 'ITEM_NAME'

			if new_label != ent['label']:
				ent['label'] = new_label

			# Keep name_ents up-to-date for subsequent entities
			if new_label == 'ITEM_NAME' and ent not in name_ents:
				name_ents.append(ent)
			elif new_label == 'ITEM_VARIANT' and ent in name_ents:
				name_ents.remove(ent)

		return entities


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
		logits_2d = outputs.logits.squeeze(0)  # [seq_len, num_labels]
		preds = logits_2d.argmax(-1).tolist()

	# Build per-word label and per-word softmax confidence dict
	word_ids = encoding.word_ids(batch_index=0)
	num_labels = logits_2d.shape[-1]
	word_labels: dict = {}
	word_conf: dict = {}  # word_id → {label_name: averaged_prob}
	word_tok_count: dict = {}
	for tok_idx, word_id in enumerate(word_ids):
		if word_id is None:
			continue
		lbl_id = preds[tok_idx]
		probs = _softmax(logits_2d[tok_idx].tolist())
		if word_id not in word_labels:
			word_labels[word_id] = ID2LABEL.get(lbl_id, 'O')
			word_conf[word_id] = {ID2LABEL.get(j, 'O'): probs[j] for j in range(num_labels)}
			word_tok_count[word_id] = 1
		else:
			# Average probabilities across sub-word tokens
			for j in range(num_labels):
				lname = ID2LABEL.get(j, 'O')
				word_conf[word_id][lname] += probs[j]
			word_tok_count[word_id] += 1

	# Normalize averaged probabilities
	for wid, cnt in word_tok_count.items():
		if cnt > 1:
			for lname in word_conf[wid]:
				word_conf[wid][lname] /= cnt

	# Group consecutive words by label; carry averaged confidence into each entity
	entities = []
	cur = None
	cur_conf_sum: dict = {}
	cur_word_count = 0
	for i, wtext in enumerate(words):
		lbl = word_labels.get(i, 'O')
		if lbl == 'O':
			if cur:
				avg_conf = {k: v / cur_word_count for k, v in cur_conf_sum.items()}
				cur['confidence'] = avg_conf
				entities.append(cur)
				cur = None
				cur_conf_sum = {}
				cur_word_count = 0
			continue
		bbox = boxes[i]
		wc = word_conf.get(i, {})
		if cur is None or cur['label'] != lbl:
			if cur:
				avg_conf = {k: v / cur_word_count for k, v in cur_conf_sum.items()}
				cur['confidence'] = avg_conf
				entities.append(cur)
			cur = {'label': lbl, 'text': wtext, 'boxes': [bbox]}
			cur_conf_sum = dict(wc)
			cur_word_count = 1
		else:
			cur['text'] += ' ' + wtext
			cur['boxes'].append(bbox)
			for k, v in wc.items():
				cur_conf_sum[k] = cur_conf_sum.get(k, 0.0) + v
			cur_word_count += 1
	if cur:
		avg_conf = {k: v / cur_word_count for k, v in cur_conf_sum.items()}
		cur['confidence'] = avg_conf
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
			q = re.sub(r"[^0-9.]", "", txt)
			if not q:
				continue
			txt = q
		# drop tiny garbage
		if len(re.sub(r"\W+", "", txt)) < 1:
			continue
		clean_entities.append({'label': e['label'], 'text': txt, 'boxes': e['boxes'], 'confidence': e.get('confidence', {})})

	def _entity_center_y(ent: dict) -> float:
		ys = [b[1] for b in ent['boxes']] + [b[3] for b in ent['boxes']]
		return (min(ys) + max(ys)) / 2.0

	def _entity_right_x(ent: dict) -> int:
		return max(b[2] for b in ent['boxes'])

	# Re-classify ITEM_NAME / ITEM_VARIANT using multi-signal robust classifier
	RobustItemClassifier().classify(clean_entities)

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
			clean_entities.append({'label': 'ITEM_PRICE', 'text': raw_val, 'boxes': [best[2]], 'confidence': {}})
			price_rows.append(clean_entities[-1])

	# Prefer one entry per label: for items we keep all, for TOTAL prefer longest/last
	final_entities = []
	for e in clean_entities:
		if e['label'].startswith('ITEM_'):
			final_entities.append(e)
	totals = [e for e in clean_entities if e['label'] == 'TOTAL']
	if totals:
		totals.sort(key=lambda x: len(re.sub(r"\D+", "", x['text'])), reverse=True)
		final_entities.append(totals[0])

	# Strip internal confidence field before returning
	for e in final_entities:
		e.pop('confidence', None)

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
		t_process_start = time.perf_counter()
		imgs = [
			'../data/CORD_1000/test/image/receipt_00099.png',
        ]
		results = [predict_image(p, model, processor, device=device) for p in imgs]
		print(json.dumps(results, indent=2, ensure_ascii=False))
		elapsed_ms = round((time.perf_counter() - t_process_start) * 1000, 2)
		print(f"TOTAL_PROCESS_MS: {elapsed_ms}")

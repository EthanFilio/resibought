import os
import json

# Paths for SROIE2019 train set (resolve relative to repository root)
# This file lives in the `ocr-sroie` folder, while `data/` is at repo root.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BOX_DIR = os.path.join(ROOT_DIR, 'data', 'SROIE2019', 'train', 'box')
ENTITIES_DIR = os.path.join(ROOT_DIR, 'data', 'SROIE2019', 'train', 'entities')
IMG_DIR = os.path.join(ROOT_DIR, 'data', 'SROIE2019', 'train', 'img')

# Collect all file ids (without extension)
def get_file_ids():
    box_files = set(os.path.splitext(f)[0] for f in os.listdir(BOX_DIR) if f.endswith('.txt'))
    ent_files = set(os.path.splitext(f)[0] for f in os.listdir(ENTITIES_DIR) if f.endswith('.txt'))
    img_files = set(os.path.splitext(f)[0] for f in os.listdir(IMG_DIR) if f.endswith('.jpg'))
    return sorted(box_files & ent_files & img_files)

# Load a single sample

def parse_box_line(line):
    # Format: x1,y1,x2,y2,x3,y3,x4,y4,text
    parts = line.strip().split(',')
    if len(parts) < 9:
        return None, None
    coords = list(map(int, parts[:8]))
    text = ','.join(parts[8:]).strip()
    # Convert 4-point box to (x0, y0, x1, y1) rectangle
    x_coords = coords[::2]
    y_coords = coords[1::2]
    x0, y0, x1, y1 = min(x_coords), min(y_coords), max(x_coords), max(y_coords)
    return text, [x0, y0, x1, y1]

def get_label(text, entities):
    # Simple rule-based matching for SROIE2019 (company, date, address, total)
    for key, value in entities.items():
        if value and value.replace(' ', '').lower() in text.replace(' ', '').lower():
            return key.upper()
    return 'O'

def load_sample(file_id):
    box_path = os.path.join(BOX_DIR, file_id + '.txt')
    ent_path = os.path.join(ENTITIES_DIR, file_id + '.txt')
    img_path = os.path.join(IMG_DIR, file_id + '.jpg')
    words = []
    boxes = []
    labels = []
    with open(ent_path, 'r', encoding='utf-8') as f:
        entities = json.load(f)
    with open(box_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            text, box = parse_box_line(line)
            if text is None or box is None:
                continue
            words.append(text)
            boxes.append(box)
            labels.append(get_label(text, entities))
    return {
        'id': file_id,
        'words': words,
        'boxes': boxes,
        'labels': labels,
        'image': img_path
    }

# Load all samples
def load_all_samples():
    file_ids = get_file_ids()
    return [load_sample(fid) for fid in file_ids]

if __name__ == '__main__':
    samples = load_all_samples()
    print(f"Loaded {len(samples)} samples from SROIE2019 train set.")
    # Example: print the first sample in LayoutLMv3 format
    if samples:
        print(json.dumps(samples[0], indent=2, ensure_ascii=False))

import json
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IMG_DIR = os.path.join(ROOT_DIR, 'data', 'CORD_1000', 'dev', 'image')
JSON_DIR = os.path.join(ROOT_DIR, 'data', 'CORD_1000', 'dev', 'json')

LABEL_MAPPING = {
    # Menu items only
    'menu.nm': 'ITEM_NAME',
    'menu.cnt': 'ITEM_QTY',
    'menu.price': 'ITEM_PRICE',
    'menu.unitprice': 'ITEM_UNITPRICE',
    'menu.discountprice': 'ITEM_DISCOUNT',
    'menu.sub_nm': 'ITEM_VARIANT',
    
    # Final total only
    'total.total_price': 'TOTAL',
    
    # Everything else → O
    'sub_total.subtotal_price': 'O',
    'sub_total.tax_price': 'O',
    'sub_total.discount_price': 'O',
    'sub_total.service_price': 'O',
    'sub_total.etc': 'O',
    'total.cashprice': 'O',
    'total.creditcardprice': 'O',
    'total.emoneyprice': 'O',
    'total.changeprice': 'O',
    'total.menuqty_cnt': 'O',
    'total.menutype_cnt': 'O',
    'total.total_etc': 'O',
    'menu.sub_cnt': 'O',
    'menu.num': 'O',
    'O': 'O'
}

# Build label list and ID mappings
LABEL_LIST = ['O', 'ITEM_NAME', 'ITEM_QTY', 'ITEM_PRICE', 'ITEM_UNITPRICE', 'ITEM_DISCOUNT', 'ITEM_VARIANT', 'TOTAL']
label2id = {l: i for i, l in enumerate(LABEL_LIST)}
id2label = {i: l for l, i in label2id.items()}

def quad_to_box(quad):
    """Convert 4-point quad coordinates to rectangular bounding box.
    
    Args:
        quad: dict with keys x1, y1, x2, y2, x3, y3, x4, y4
    
    Returns:
        [x0, y0, x1, y1] where (x0, y0) is top-left, (x1, y1) is bottom-right
    """
    try:
        x_coords = [quad['x1'], quad['x2'], quad['x3'], quad['x4']]
        y_coords = [quad['y1'], quad['y2'], quad['y3'], quad['y4']]
        x0 = min(x_coords)
        y0 = min(y_coords)
        x1 = max(x_coords)
        y1 = max(y_coords)
        return [x0, y0, x1, y1]
    except (KeyError, TypeError, ValueError):
        return None

def get_file_ids():
    image_files = set(os.path.splitext(f)[0] for f in os.listdir(IMG_DIR) if f.endswith('.png'))
    json_files =  set(os.path.splitext(f)[0] for f in os.listdir(JSON_DIR) if f.endswith('.json'))
    return sorted(image_files & json_files)

def load_sample(file_id):
    img_path = os.path.join(IMG_DIR, file_id + '.png')
    json_path = os.path.join(JSON_DIR, file_id + '.json')

    words = []
    boxes = []
    labels = []

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for line in data["valid_line"]:
        # Extract category and map to label
        category = line.get('category', 'O')
        mapped_label = LABEL_MAPPING.get(category, 'O')
        label_id = label2id[mapped_label]
        
        # Process each word in the line
        word_items = line.get('words', [])
        for word_item in word_items:
            # Extract word text
            text = word_item.get('text', '').strip()
            if not text:
                continue
            
            # Extract and convert quad to box
            quad = word_item.get('quad', {})
            box = quad_to_box(quad)
            if box is None:
                continue
            
            # Append to lists
            words.append(text)
            boxes.append(box)
            labels.append(label_id)

    return  {
        'id': file_id,
        'words': words,
        'boxes': boxes,
        'labels': labels,
        'image': img_path,
    }

def load_all_samples():
    file_ids = get_file_ids()
    return [load_sample(fid) for fid in file_ids]

if __name__ == '__main__':
    samples = load_all_samples()
    print(f"Loaded {len(samples)} from CORD_1000 train set")
    
    if samples:
        print(json.dumps(samples[0], indent=2, ensure_ascii=False))
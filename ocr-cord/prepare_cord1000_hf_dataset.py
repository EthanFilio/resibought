from cord1000_train_loader import load_all_samples as load_train_samples
from cord1000_val_loader import load_all_samples as load_val_samples
from cord1000_test_loader import load_all_samples as load_test_samples

from transformers import LayoutLMv3Processor

import datasets
import PIL

LABEL_LIST = ['O', 'ITEM_NAME', 'ITEM_QTY', 'ITEM_PRICE', 'ITEM_UNITPRICE', 'ITEM_DISCOUNT', 'ITEM_VARIANT', 'TOTAL']
label2id = {l: i for i, l in enumerate(LABEL_LIST)}
id2label = {i: l for l, i in label2id.items()}

def prepare_hf_dataset(samples):
    data = {
        'id': [], 'words': [], 'boxes': [], 'labels': [], 'image_path': []
    }
    for s in samples:
        data['id'].append(s['id'])
        data['words'].append(s['words'])
        data['boxes'].append(s['boxes'])
        data['labels'].append(s['labels'])  # labels already are integer IDs from loaders
        data['image_path'].append(s['image'])
    return datasets.Dataset.from_dict(data)

def encode_batch(batch, processor):
    images = [PIL.Image.open(path).convert('RGB') for path in batch['image_path']]
    # Normalize boxes to 0-1000 coordinate space required by LayoutLMv3
    norm_boxes_batch = []
    for img, boxes in zip(images, batch['boxes']):
        w, h = img.size
        norm_boxes = []
        for box in boxes:
            x0, y0, x1, y1 = box
            nx0 = int(round(max(0, min(1000, x0 / w * 1000))))
            ny0 = int(round(max(0, min(1000, y0 / h * 1000))))
            nx1 = int(round(max(0, min(1000, x1 / w * 1000))))
            ny1 = int(round(max(0, min(1000, y1 / h * 1000))))
            norm_boxes.append([nx0, ny0, nx1, ny1])
        norm_boxes_batch.append(norm_boxes)

    # Let the processor align word-level labels to token-level labels
    # and return plain Python lists (avoid returning tensors here so the
    # dataset saved to disk contains serializable lists).
    encoding = processor(
        images,
        batch['words'],
        boxes=norm_boxes_batch,
        word_labels=batch['labels'],
        truncation=True,
        padding='max_length',
        max_length=512,
    )

    # Ensure all fields are plain python lists (datasets will accept them)
    out = {}
    for k, v in encoding.items():
        try:
            out[k] = v.tolist() if hasattr(v, 'tolist') else v
        except Exception:
            out[k] = v
    return out


def build_dataset():
    # Prepare train dataset
    train_samples = load_train_samples()
    train_dataset = prepare_hf_dataset(train_samples)
    processor = LayoutLMv3Processor.from_pretrained('microsoft/layoutlmv3-base', apply_ocr=False)
    train_dataset = train_dataset.map(lambda x: encode_batch(x, processor), batched=True, batch_size=4)
    train_dataset.save_to_disk('cord1000_hf_train_dataset')
    print('Train dataset prepared and saved.')

    # Prepare validation dataset
    val_samples = load_val_samples()
    val_dataset = prepare_hf_dataset(val_samples)
    val_dataset = val_dataset.map(lambda x: encode_batch(x, processor), batched=True, batch_size=4)
    val_dataset.save_to_disk('cord1000_hf_val_dataset')
    print('Validation dataset prepared and saved.')

    # Prepare test dataset
    test_samples = load_test_samples()
    test_dataset = prepare_hf_dataset(test_samples)
    test_dataset = test_dataset.map(lambda x: encode_batch(x, processor), batched=True, batch_size=4)
    test_dataset.save_to_disk('cord1000_hf_test_dataset')
    print('Test dataset prepared and saved.')

if __name__ == '__main__':
    build_dataset()
import os
import json
from datasets import Dataset
from sroie2019_train_loader import load_all_samples as load_train_samples
from sroie2019_test_loader import load_all_samples as load_test_samples
from transformers import LayoutLMv3Processor
from PIL import Image

def get_label_list(samples):
    labels = set()
    for s in samples:
        labels.update(s['labels'])
    labels.discard('O')
    return ['O'] + sorted(labels)

def prepare_hf_dataset(samples, label_list):
    label2id = {l: i for i, l in enumerate(label_list)}
    data = {
        'id': [], 'words': [], 'boxes': [], 'labels': [], 'image_path': []
    }
    for s in samples:
        data['id'].append(s['id'])
        data['words'].append(s['words'])
        data['boxes'].append(s['boxes'])
        data['labels'].append([label2id[l] for l in s['labels']])
        data['image_path'].append(s['image'])
    return Dataset.from_dict(data)

def encode_batch(batch, processor, label_all_tokens=True):
    images = [Image.open(path).convert('RGB') for path in batch['image_path']]
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

    encoding = processor(
        images,
        batch['words'],
        boxes=norm_boxes_batch,
        word_labels=batch['labels'],
        truncation=True,
        padding='max_length',
        max_length=512,
        return_tensors='pt'
    )
    return {k: v for k, v in encoding.items()}

def main():
    # Prepare train dataset
    train_samples = load_train_samples()
    label_list = get_label_list(train_samples)
    train_dataset = prepare_hf_dataset(train_samples, label_list)
    processor = LayoutLMv3Processor.from_pretrained('microsoft/layoutlmv3-base', apply_ocr=False)
    train_dataset = train_dataset.map(lambda x: encode_batch(x, processor), batched=True, batch_size=4)
    train_dataset.save_to_disk('sroie2019_hf_dataset')
    print('Train dataset prepared and saved.')

    # Prepare test dataset
    test_samples = load_test_samples()
    test_dataset = prepare_hf_dataset(test_samples, label_list)
    test_dataset = test_dataset.map(lambda x: encode_batch(x, processor), batched=True, batch_size=4)
    test_dataset.save_to_disk('sroie2019_hf_test_dataset')
    print('Test dataset prepared and saved.')

if __name__ == '__main__':
    main()

import os
import datasets
import torch

from datasets import load_from_disk
from prepare_cord1000_hf_dataset import build_dataset
from cord1000_train_loader import (
    LABEL_LIST as CORD_LABEL_LIST,
    label2id as CORD_label2id,
)

from transformers import (
    LayoutLMv3ForTokenClassification,
    LayoutLMv3Processor,
    TrainingArguments,
    Trainer,
    default_data_collator,
)

TRAIN_PATH = "cord1000_hf_train_dataset"
VALIDATE_PATH = "cord1000_hf_val_dataset"
TEST_PATH = "cord1000_hf_test_dataset"

MODEL_OUTPUT_DIR = "layoutlmv3-cord1000"
FINAL_MODEL_DIR = "layoutlmv3-cord1000-final"


def is_completely_preprocessed(dataset):

    if dataset is None or len(dataset) == 0:
        return False

    required_cols = {
        'input_ids',
        'attention_mask',
        'bbox',
        'labels'
    }

    if not required_cols.issubset(set(dataset.column_names)):
        return False

    try:
        sample = dataset[0]

        if len(sample['input_ids']) == 0:
            return False

        if len(sample['bbox']) == 0:
            return False

        return True

    except Exception:
        return False


def validate_dataset(dataset, name, label_list):

    print(f"\nValidating dataset: {name}")

    if dataset is None or len(dataset) == 0:
        print("✗ Empty dataset")
        return False

    required_cols = {
        'input_ids',
        'attention_mask',
        'bbox',
        'labels'
    }

    cols = set(dataset.column_names)

    if not required_cols.issubset(cols):
        print(f"✗ Missing columns: {required_cols - cols}")
        return False

    sample_count = min(10, len(dataset))

    for i in range(sample_count):

        sample = dataset[i]

        labels = sample.get('labels', [])

        if not isinstance(labels, (list, tuple)):
            print(f"✗ Labels not list at sample {i}")
            return False

        for label in labels:

            if label == -100:
                continue

            if not isinstance(label, int):
                print(f"✗ Non-int label at sample {i}")
                return False

            if not (0 <= label < len(label_list)):
                print(f"✗ Label out of range at sample {i}: {label}")
                return False

        bboxes = sample.get('bbox', [])

        for bbox in bboxes:

            if not (
                isinstance(bbox, (list, tuple))
                and len(bbox) == 4
            ):
                print(f"✗ Invalid bbox format at sample {i}")
                return False

            if not all(isinstance(x, int) for x in bbox):
                print(f"✗ Non-int bbox at sample {i}")
                return False

            if not all(0 <= x <= 1000 for x in bbox):
                print(f"✗ Bbox out of normalized range at sample {i}")
                return False

    print(f"✓ {name} valid ({len(dataset)} samples)")
    return True


def preprocess_dataset():

    try:

        train_data = datasets.load_from_disk(TRAIN_PATH)
        val_data = datasets.load_from_disk(VALIDATE_PATH)
        test_data = datasets.load_from_disk(TEST_PATH)

        all_valid = all(map(
            is_completely_preprocessed,
            [train_data, val_data, test_data]
        ))

        if all_valid:
            print("✔ Preprocessed datasets loaded successfully.")
            return train_data, val_data, test_data

        print("⚠ Datasets found but invalid. Reprocessing...")

    except FileNotFoundError:
        print("⚠ Processed datasets not found.")

    except Exception as e:
        print(f"⚠ Error loading datasets: {e}")

    print("⚙ Running preprocessing pipeline...")
    return build_dataset()


def main():

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    print(f"\nUsing device: {device}")

    if device == 'cuda':
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Version: {torch.version.cuda}")

    preprocess_dataset()

    assert os.path.isdir(TRAIN_PATH), "Missing train dataset"
    assert os.path.isdir(VALIDATE_PATH), "Missing validation dataset"
    assert os.path.isdir(TEST_PATH), "Missing test dataset"

    train_dataset = load_from_disk(TRAIN_PATH)
    val_dataset = load_from_disk(VALIDATE_PATH)
    test_dataset = load_from_disk(TEST_PATH)

    label_list = CORD_LABEL_LIST
    label2id = CORD_label2id
    id2label = {i: l for i, l in enumerate(label_list)}

    train_ok = validate_dataset(
        train_dataset,
        "train",
        label_list
    )

    val_ok = validate_dataset(
        val_dataset,
        "validation",
        label_list
    )

    test_ok = validate_dataset(
        test_dataset,
        "test",
        label_list
    )

    if not (train_ok and val_ok and test_ok):
        raise RuntimeError(
            "Dataset validation failed. Aborting training."
        )

    processor = LayoutLMv3Processor.from_pretrained(
        'microsoft/layoutlmv3-base',
        apply_ocr=False
    )

    model = LayoutLMv3ForTokenClassification.from_pretrained(
        'microsoft/layoutlmv3-base',
        num_labels=len(label_list),
        id2label=id2label,
        label2id=label2id
    )

    train_batch_size = 2 if device == 'cpu' else 4
    eval_batch_size = 2 if device == 'cpu' else 4

    print(
        f"\nBatch sizes:"
        f" train={train_batch_size}"
        f" eval={eval_batch_size}"
    )

    training_args = TrainingArguments(
        output_dir=MODEL_OUTPUT_DIR,
        per_device_train_batch_size=train_batch_size,
        per_device_eval_batch_size=eval_batch_size,
        learning_rate=5e-5,
        weight_decay=0.01,
        warmup_ratio=0.1,
        num_train_epochs=10,
        eval_strategy='steps',
        eval_steps=200,
        save_steps=200,
        save_total_limit=3,
        logging_steps=20,
        load_best_model_at_end=True,
        metric_for_best_model='eval_loss',
        greater_is_better=False,
        fp16=(device == 'cuda'),
        dataloader_num_workers=2,
        gradient_accumulation_steps=1,
        report_to='none',
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        processing_class=processor,
        data_collator=default_data_collator,
    )

    print("\nStarting training...\n")

    trainer.train()

    print("\nRunning final test evaluation...\n")

    test_results = trainer.evaluate(test_dataset)

    print("\nTest Results:")
    for key, value in test_results.items():
        print(f"{key}: {value}")

    trainer.save_model(FINAL_MODEL_DIR)
    processor.save_pretrained(FINAL_MODEL_DIR)

    print("\n✔ Training complete.")
    print(f"✔ Model saved to: {FINAL_MODEL_DIR}")

if __name__ == '__main__':
    main()
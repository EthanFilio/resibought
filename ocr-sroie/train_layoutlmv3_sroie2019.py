from datasets import load_from_disk
from transformers import (
    LayoutLMv3ForTokenClassification,
    LayoutLMv3Processor,
    TrainingArguments,
    Trainer,
    default_data_collator,
)

def main():
    # Load train and test datasets
    train_dataset = load_from_disk('sroie2019_hf_dataset')
    test_dataset = load_from_disk('sroie2019_hf_test_dataset')  # Make sure to prepare this as you did for train
    label_list = ['O', 'ADDRESS', 'COMPANY', 'DATE', 'TOTAL']  # Adjust if needed
    id2label = {i: l for i, l in enumerate(label_list)}
    label2id = {l: i for i, l in enumerate(label_list)}

    # Load processor and model
    processor = LayoutLMv3Processor.from_pretrained('microsoft/layoutlmv3-base', apply_ocr=False)
    model = LayoutLMv3ForTokenClassification.from_pretrained(
        'microsoft/layoutlmv3-base',
        num_labels=len(label_list),
        id2label=id2label,
        label2id=label2id
    )

    data_collator = default_data_collator

    # Training arguments
    training_args = TrainingArguments(
        output_dir='layoutlmv3-sroie2019-faster',
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        num_train_epochs=3,
        eval_strategy='steps',
        eval_steps=50,
        save_steps=100,
        logging_steps=10,
        learning_rate=5e-5,
        save_total_limit=2,
        report_to='none',
        fp16=True,
        dataloader_num_workers=2,
        gradient_accumulation_steps=1,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset, # type: ignore
        eval_dataset=test_dataset, # type: ignore
        processing_class=processor,
        data_collator=data_collator,
    )

    trainer.train()
    trainer.save_model('layoutlmv3-sroie2019-final-faster')
    print('Training complete. Model saved.')

if __name__ == '__main__':
    main()

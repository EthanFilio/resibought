## OCR SROIE Utilities

Brief descriptions of the Python scripts in the `ocr-sroie/` folder.

- `prepare_sroie2019_hf_dataset.py`: Prepare Hugging Face datasets from SROIE2019 train/test loaders and save them to disk (`sroie2019_hf_dataset`, `sroie2019_hf_test_dataset`). Uses LayoutLMv3Processor to encode images, words, and normalized boxes.
- `sroie2019_train_loader.py`: Load SROIE2019 training samples (boxes, entities, images), convert 4-point boxes to rectangular boxes, and assign token labels.
- `sroie2019_test_loader.py`: Same as the train loader but for the test split; includes robust file-encoding fallbacks and safer file reads.
- `train_layoutlmv3_sroie2019.py`: Train a LayoutLMv3 token-classification model using the prepared HF datasets and Hugging Face Trainer. Saves checkpoints to layoutlmv3-sroie2019 and the final model to layoutlmv3-sroie2019-final.
- `scan_and_extract.py`: Inference helper, which essentially runs Tesseract OCR on an image, normalizes boxes, applies a trained LayoutLMv3 token-classifier to predict labels, and groups token-level predictions into entity spans.

Note: `LayoutLMv3Processor` is just a preprocessing helper; the token-classification model itself (i.e. `LayoutLMv3ForTokenClassification`) is the actual trained neural network itself that makes predictions!

<br/>

## Setup

1. Make sure you have a Python environment activated. It's better if it's in the root of this repo since there will be other models running on Python.
2. Installing Python requirements:
    ```
    pip install -r requirements.txt
    ```
    Note: if you want to train on a PC with a GPU (say `nvidia-smi`), uninstall `torch`, then do `pip install torch --index-url https://download.pytorch.org/whl/cu118`

3. Install [`tesseract` engine](https://github.com/UB-Mannheim/tesseract/wiki) since we use `pytesseract`. I think the link is only for Windows.
4. Make sure `SROIE2019/` dataset is present in the Resibought root folder `data/` (i.e. `./data/SROIE2019/`).
5. 
    At first hand, we still don't have the preprocessed HuggingFace. This is because Github has limitations to file sizes. If we ever decide on preprocessing and training it again, just run the commands below:
    ```
    python prepare_sroie2019_hf_dataset.py
    ...
    ```
    After this, `sroie2019_hf_dataset/` and `sroie2019_hf_test_dataset/` should be present now under `ocr-sroie`. Then run,
    ```
    python train_layoutlmv3_sroie2019.py
    ...
    ```

    **NOTE: I could just transfer the pretrained files over the cloud since I'm running them already (*by the time I'm writing this README*), so we don't have to do this step again.**

6. To test, play with `scan_and_extract.py`.


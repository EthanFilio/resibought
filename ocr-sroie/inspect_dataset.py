from datasets import load_from_disk
from collections import Counter

DS_PATH = 'sroie2019_hf_dataset'

def main():
    ds = load_from_disk(DS_PATH)
    # Try to print the label mapping used when preparing the HF dataset
    try:
        from sroie2019_train_loader import load_all_samples
        from prepare_sroie2019_hf_dataset import get_label_list
        samples = load_all_samples()
        label_list = get_label_list(samples)
        label2id = {l: i for i, l in enumerate(label_list)}
        print('label_list:', label_list)
        print('label2id:', label2id)
    except Exception as e:
        print('Could not build label mapping:', e)
    cnt = Counter()
    n = 0
    for ex in ds:
        n += 1
        labs = ex.get('labels') or ex.get('label')
        if labs is None:
            continue
        # labs may be a list of ints or nested tensors; flatten
        try:
            for l in labs:
                cnt[int(l)] += 1
        except Exception:
            pass
    print(f"Loaded {n} examples from {DS_PATH}")
    print('Label id counts (top 20):')
    for k, v in cnt.most_common(20):
        print(f"{k}: {v}")

    # print a few examples
    print('\nSample examples:')
    for i in range(3):
        ex = ds[i]
        print('---')
        print('image:', ex.get('image') or ex.get('image_path'))
        print('words:', ex.get('words')[:50])
        print('labels:', ex.get('labels')[:50])

if __name__ == '__main__':
    main()

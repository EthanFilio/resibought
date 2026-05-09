import torch
import paddleocr

if __name__ == '__main__':

    # Use GPU instead of CPU is device has former; otherwise, just use CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"

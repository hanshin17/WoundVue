"""
Pengujian Model — inference on the test split with the trained .keras models (trained on Kaggle).
Reports accuracy, per-class precision/recall/F1, confusion matrix, and compares the classifier input modes
(original / masked / crop) after U-Net segmentation.

Run:  python tests/evaluate_models.py [path/to/Dataset_Split_Zip.zip]
"""
import io
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

from utils import classification, config, segmentation  # noqa: E402


def load_test_set(zip_path):
    z = zipfile.ZipFile(zip_path)
    files = [n for n in z.namelist() if n.startswith("test/") and not n.endswith("/")]
    folders = sorted({n.split("/")[1] for n in files})
    imgs, labels = [], []
    for n in files:
        try:
            imgs.append(Image.open(io.BytesIO(z.read(n))).convert("RGB"))
            labels.append(folders.index(n.split("/")[1]))
        except Exception:
            pass
    return imgs, np.array(labels), folders


def report(y, pred, names):
    k = len(names)
    cm = np.zeros((k, k), int)
    for t, p in zip(y, pred):
        cm[t, p] += 1
    print(f"\n{'Class':18s} {'Prec':>6s} {'Recall':>6s} {'F1':>6s} {'N':>4s}")
    for i, n in enumerate(names):
        tp = cm[i, i]
        prec = tp / cm[:, i].sum() if cm[:, i].sum() else 0
        rec = tp / cm[i].sum() if cm[i].sum() else 0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0
        print(f"{n:18s} {prec:6.3f} {rec:6.3f} {f1:6.3f} {cm[i].sum():4d}")
    short = [n[:6] for n in names]
    print("\nConfusion matrix (rows = true, cols = predicted)")
    print(" " * 8 + " ".join(f"{s:>6}" for s in short))
    for i in range(k):
        print(f"{short[i]:>7} " + " ".join(f"{v:6d}" for v in cm[i]))


def main():
    zip_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "Dataset_Split_Zip.zip")
    imgs, y, folders = load_test_set(zip_path)
    print(f"Test images: {len(imgs)}  classes: {len(folders)}")

    segs = [segmentation.segment(im) for im in imgs]
    found = np.mean([s["found"] for s in segs if s]) if segs[0] else 0
    print(f"U-Net found a wound in {found:.1%} of test images")

    model = classification.load_model()
    results = {}
    for mode in ("original", "masked", "crop"):
        X = np.concatenate([classification.prepare_input(im, s, mode) for im, s in zip(imgs, segs)])
        pred = model.predict(X, verbose=0, batch_size=32).argmax(1)
        results[mode] = pred
        print(f"Accuracy [{mode:8s}] = {(pred == y).mean():.4f}")

    print(f"\nDetailed report for CLASSIFY_INPUT = '{config.CLASSIFY_INPUT}':")
    report(y, results[config.CLASSIFY_INPUT], config.CLASS_NAMES)


if __name__ == "__main__":
    main()

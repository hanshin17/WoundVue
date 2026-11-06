"""Step 2 — Classification with the best transfer-learning model (10 wound classes)."""
import keras
import numpy as np
from PIL import Image

from . import config

_model = None


def load_model():
    global _model
    if _model is None:
        print(f"[classification] Loading classifier: {config.CLASSIFIER_PATH}")
        _model = keras.models.load_model(config.CLASSIFIER_PATH, compile=False)
    return _model


def prepare_input(img: Image.Image, seg: dict | None, mode: str = config.CLASSIFY_INPUT) -> np.ndarray:
    """Build the classifier input (1, 224, 224, 3), raw 0-255, using the U-Net result according to `mode`."""
    size = config.IMG_SIZE
    base = np.asarray(img.resize((size, size)), dtype=np.float32)
    if seg is None or not seg["found"] or mode == "original":
        return base[None]
    if mode == "masked":
        return (base * seg["mask"][..., None])[None]
    if mode == "crop":
        x0, y0, x1, y1 = seg["bbox"]
        pad = int(max(x1 - x0, y1 - y0) * 0.25) + 8
        box = (max(0, x0 - pad), max(0, y0 - pad), min(size, x1 + pad), min(size, y1 + pad))
        crop = Image.fromarray(base.astype(np.uint8)).crop(box).resize((size, size))
        return np.asarray(crop, dtype=np.float32)[None]
    raise ValueError(f"Unknown CLASSIFY_INPUT mode: {mode}")


def classify(x: np.ndarray) -> dict:
    probs = load_model().predict(x, verbose=0)[0]
    idx = int(np.argmax(probs))
    ranked = sorted(
        ({"name": config.CLASS_NAMES[i], "prob": float(p) * 100} for i, p in enumerate(probs)),
        key=lambda d: d["prob"],
        reverse=True,
    )
    return {
        "index": idx,
        "label": config.CLASS_NAMES[idx],
        "confidence": float(probs[idx]) * 100,
        "probabilities": ranked,
    }

"""Step 1 — Segmentation with U-Net: produce a binary mask isolating the wound from healthy skin."""
import os

import keras
import numpy as np
from PIL import Image

from . import config

_unet = None


def load_model():
    global _unet
    if _unet is None and os.path.exists(config.UNET_PATH):
        print(f"[segmentation] Loading U-Net: {config.UNET_PATH}")
        _unet = keras.models.load_model(config.UNET_PATH, compile=False)  # custom bce_dice_loss not needed
    return _unet


def segment(img: Image.Image) -> dict | None:
    """Returns dict with binary mask (224x224 uint8 0/1), area %, bbox, mask/overlay images; None if U-Net missing."""
    unet = load_model()
    if unet is None:
        return None

    size = config.IMG_SIZE
    x = np.asarray(img.resize((size, size)), dtype=np.float32)[None] / 255.0
    prob = unet.predict(x, verbose=0)[0, ..., 0]
    mask = (prob > config.MASK_THRESHOLD).astype(np.uint8)
    area = float(mask.mean())
    found = area >= config.MIN_WOUND_AREA

    bbox = None
    if found:
        ys, xs = np.where(mask)
        bbox = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))

    mask_img = Image.fromarray(mask * 255).convert("L").resize((size, size), Image.NEAREST)
    return {
        "mask": mask,
        "area_percent": area * 100,
        "found": found,
        "bbox": bbox,
        "mask_image": mask_img,
        "overlay_image": mask_img.convert("RGB"),
    }

"""Step 3 — Grad-CAM: heatmap of the regions the classifier focused on, overlaid on the original image."""
import cv2
import keras
import numpy as np
import tensorflow as tf
from PIL import Image

from . import config
from .classification import load_model

_grad_model = None


def _get_grad_model():
    global _grad_model
    if _grad_model is None:
        model = load_model()
        _grad_model = keras.Model(
            inputs=model.inputs,
            outputs=[model.get_layer(config.LAST_CONV_LAYER).output, model.output],
        )
    return _grad_model


def compute_heatmap(x: np.ndarray, class_idx: int) -> np.ndarray:
    """Gradients of the class score w.r.t. the last conv layer -> normalized heatmap in [0, 1]."""
    with tf.GradientTape() as tape:
        conv_out, preds = _get_grad_model()(tf.convert_to_tensor(x), training=False)
        score = preds[:, class_idx]
    grads = tape.gradient(score, conv_out)
    weights = tf.reduce_mean(grads, axis=(0, 1, 2))
    cam = tf.nn.relu(tf.reduce_sum(conv_out[0] * weights, axis=-1)).numpy()
    return cam / cam.max() if cam.max() > 0 else cam


def overlay(img: Image.Image, heatmap: np.ndarray, size=(config.IMG_SIZE, config.IMG_SIZE), alpha: float = 0.45) -> Image.Image:
    base = np.asarray(img.resize(size))
    heat = cv2.resize(heatmap.astype(np.float32), size)
    heat = cv2.applyColorMap(np.uint8(255 * heat), cv2.COLORMAP_JET)
    heat = cv2.cvtColor(heat, cv2.COLOR_BGR2RGB)
    return Image.fromarray(cv2.addWeighted(base, 1 - alpha, heat, alpha, 0))

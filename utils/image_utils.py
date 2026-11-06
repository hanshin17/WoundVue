"""Shared image helpers."""
import base64
import io
import os

import cv2
import numpy as np
from PIL import Image, ImageOps

from . import config


def load_image(stream) -> Image.Image:
    """Open an uploaded image, apply EXIF rotation, convert to RGB, and resize to 224x224."""
    img = Image.open(stream)
    img = ImageOps.exif_transpose(img)
    return img.convert("RGB").resize((config.IMG_SIZE, config.IMG_SIZE))


def skin_pixel_ratio(img: Image.Image) -> float:
    """Estimate fraction of pixels matching human skin tones in YCrCb / HSV color space."""
    arr = np.asarray(img.convert("RGB"))
    ycrcb = cv2.cvtColor(arr, cv2.COLOR_RGB2YCrCb)
    hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
    m_ycrcb = (
        (ycrcb[:, :, 1] >= 133) & (ycrcb[:, :, 1] <= 180)
        & (ycrcb[:, :, 2] >= 77) & (ycrcb[:, :, 2] <= 135)
    )
    m_hsv = (
        (hsv[:, :, 0] <= 25)
        & (hsv[:, :, 1] >= 15) & (hsv[:, :, 1] <= 180)
        & (hsv[:, :, 2] >= 60)
    )
    return float((m_ycrcb | m_hsv).mean())


def has_portrait_face(img: Image.Image) -> bool:
    """Detect whether the image contains a human face portrait/selfie using OpenCV Haar cascades."""
    try:
        gray = cv2.cvtColor(np.asarray(img.convert("RGB")), cv2.COLOR_RGB2GRAY)
        cascade_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
        detector = cv2.CascadeClassifier(cascade_path)
        faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(36, 36))
        return len(faces) > 0
    except Exception:
        return False


def to_data_uri(img: Image.Image, fmt: str = "JPEG") -> str:
    buf = io.BytesIO()
    img.save(buf, format=fmt, quality=90) if fmt == "JPEG" else img.save(buf, format=fmt)
    return f"data:image/{fmt.lower()};base64," + base64.b64encode(buf.getvalue()).decode()

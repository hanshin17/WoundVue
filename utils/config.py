"""Central configuration: paths, class names, and settings loaded from .env."""
import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, ".env.example"), override=False)

# ---- Models (trained on Kaggle, stored in models/) ----
MODELS_DIR = os.path.join(BASE_DIR, "models")
CLASSIFIER_PATH = os.path.join(MODELS_DIR, "classifier_efficientnet.keras")
UNET_PATH = os.path.join(MODELS_DIR, "unet_segmentation.keras")

IMG_SIZE = 224

# Classifier: EfficientNet, input raw 0-255 (Rescaling/Normalization layers are inside the model)
CLASSIFIER_NAME = "EfficientNet"
LAST_CONV_LAYER = "top_activation"  # used by Grad-CAM

# IMPORTANT: must match the class index order used during training
# (alphabetical order of the dataset folder names).
CLASS_NAMES = [
    "Abrasions",        # Dataset_Luka_Fix_ABRASI
    "Burns",            # Dataset_Luka_Fix_Bakar
    "Cut",              # Dataset_Luka_Fix_Cut
    "Laceration",       # Dataset_Luka_Fix_Laseration
    "Bruises",          # Dataset_Luka_Fix_Memar
    "Diabetic Wounds",  # Diabetic Wounds
    "Normal Skin",      # Normal
    "Pressure Wounds",  # Pressure Wounds
    "Surgical Wounds",  # Surgical Wounds
    "Venous Wounds",    # Venous Wounds
]

# U-Net: input scaled to [0, 1], output sigmoid mask
MASK_THRESHOLD = 0.5
MIN_WOUND_AREA = 0.0005  # 0.05% (~25 pixels on 224x224) so thin cuts/lacerations are still detected

# Which image is fed to the classifier after segmentation:
#   "original" - full original image (what the classifier was trained on)
#   "masked"   - background outside the U-Net mask set to black
#   "crop"     - crop around the U-Net mask (isolated wound area + small margin)
CLASSIFY_INPUT = os.getenv("CLASSIFY_INPUT", "original")

# ---- LLM (Gemini) ----
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
# Automatic fallback chain when a model hits free-tier rate/quota limits (429 / 503)
GEMINI_FALLBACK_MODELS = [
    GEMINI_MODEL,
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
]

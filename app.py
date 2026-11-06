"""
WoundVue — Flask main application.

Pipeline per uploaded image:
    1. Segmentation  (U-Net)              -> utils/segmentation.py
    2. Classification (transfer learning) -> utils/classification.py
    3. Grad-CAM visualization             -> utils/gradcam.py
    4. LLM recommendation (Gemini)        -> utils/llm.py
    5. Results returned to the front-end  (templates/index.html, static/)

Run:
    python app.py        (or: flask run)
Then open http://127.0.0.1:5000
"""
import numpy as np
from flask import Flask, jsonify, render_template, request
from PIL import Image

from utils import classification, config, gradcam, llm, segmentation
from utils.image_utils import has_portrait_face, load_image, skin_pixel_ratio, to_data_uri

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB upload limit (matches UI)

# Load and warm up models once at startup so the first upload has zero cold-start delay
classification.load_model()
segmentation.load_model()
try:
    _dummy_img = Image.new("RGB", (config.IMG_SIZE, config.IMG_SIZE), (128, 128, 128))
    _dummy_seg = segmentation.segment(_dummy_img)
    _dummy_x = classification.prepare_input(_dummy_img, _dummy_seg)
    classification.classify(_dummy_x)
except Exception:
    pass
print(f"[app] Classifier input mode: {config.CLASSIFY_INPUT}")
print(f"[app] Gemini: {'configured (' + config.GEMINI_MODEL + ')' if llm.is_configured() else 'NOT configured - set GEMINI_API_KEY in .env'}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/predict", methods=["POST"])
def predict():
    # Input from the user
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    try:
        img = load_image(request.files["image"].stream)
    except Exception:
        return jsonify({"error": "Invalid image file"}), 400

    # 1. Segmentation (U-Net)
    try:
        seg = segmentation.segment(img)
    except Exception as e:
        print("[app] U-Net error:", e)
        seg = None

    # 2. Classification
    x = classification.prepare_input(img, seg)
    cls = classification.classify(x)

    # 3. Grad-CAM (overlaid on the image that was fed to the classifier)
    try:
        heatmap = gradcam.compute_heatmap(x, cls["index"])
        gradcam_img = gradcam.overlay(Image.fromarray(x[0].astype(np.uint8)), heatmap)
        gradcam_area = round(float((heatmap >= 0.5).mean() * 100), 1)
    except Exception as e:
        print("[app] Grad-CAM error:", e)
        gradcam_img = None
        gradcam_area = None

    # 4. LLM recommendation & multimodal visual verification (Gemini 3.5 Flash)
    recommendation = llm.generate_recommendation(img, cls, seg, gradcam_img)

    # Determine whether the image is a valid wound, normal skin, or a non-wound object:
    unet_found = seg["found"] if seg else True
    skin_ratio = skin_pixel_ratio(img)

    if recommendation is not None:
        # Gemini visually verified the image
        if not recommendation.get("is_valid_skin_or_wound", True):
            is_wound = False
            recommendation = None
        else:
            is_wound = True
            if recommendation.get("is_normal_skin", False):
                # Extra safeguard: a genuine close-up of normal skin must be mostly skin tone (>= 60%)
                if skin_ratio < 0.60:
                    is_wound = False
                    recommendation = None
                elif cls["label"] != "Normal Skin":
                    normal_idx = config.CLASS_NAMES.index("Normal Skin")
                    cls["index"] = normal_idx
                    cls["label"] = "Normal Skin"
                    cls["confidence"] = round(max(cls["confidence"], skin_ratio * 100, 95.0), 1)
                    for item in cls["probabilities"]:
                        if item["name"] == "Normal Skin":
                            item["prob"] = cls["confidence"]
                        else:
                            item["prob"] = round(item["prob"] * (100 - cls["confidence"]) / 100, 1)
                    cls["probabilities"].sort(key=lambda d: d["prob"], reverse=True)
    else:
        # Offline fallback if all Gemini models are unreachable:
        #   1. Reject portrait/selfie photos containing a face when confidence is low (< 85%)
        #   2. Reject images with little human skin tone (< 25%)
        #   3. Require either high classifier confidence (>= 80%) OR a close-up of skin (>= 65% skin pixels)
        if has_portrait_face(img) and cls["confidence"] < 85:
            is_wound = False
        elif skin_ratio < 0.25:
            is_wound = False
        elif not unet_found and cls["label"] != "Normal Skin" and cls["confidence"] < 90:
            if skin_ratio >= 0.65:
                normal_idx = config.CLASS_NAMES.index("Normal Skin")
                cls["index"] = normal_idx
                cls["label"] = "Normal Skin"
                cls["confidence"] = round(max(cls["confidence"], skin_ratio * 100), 1)
                for item in cls["probabilities"]:
                    if item["name"] == "Normal Skin":
                        item["prob"] = cls["confidence"]
                    else:
                        item["prob"] = round(item["prob"] * (100 - cls["confidence"]) / 100, 1)
                cls["probabilities"].sort(key=lambda d: d["prob"], reverse=True)
                is_wound = True
            else:
                is_wound = False
        elif cls["confidence"] < 75:
            is_wound = False
        else:
            is_wound = True

    # 5. Output to front-end (all images standardized to 224x224)
    return jsonify({
        "predicted": cls["label"],
        "confidence": cls["confidence"],
        "probabilities": cls["probabilities"],
        "is_wound": is_wound,
        "classify_input": config.CLASSIFY_INPUT,
        "original": to_data_uri(img, "JPEG"),
        "mask": to_data_uri(seg["mask_image"], "PNG") if seg else None,
        "mask_overlay": to_data_uri(seg["overlay_image"], "PNG") if seg else None,
        "wound_area": seg["area_percent"] if seg else None,
        "gradcam": to_data_uri(gradcam_img) if gradcam_img else None,
        "gradcam_area": gradcam_area,
        "recommendation": recommendation,  # None -> front-end falls back to built-in text
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)

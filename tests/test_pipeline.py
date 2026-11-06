"""
Pengujian Fungsional — checks that every module (segmentation, classification, Grad-CAM, LLM)
works and that they are connected through the Flask endpoint.

Run:  python tests/test_pipeline.py [path/to/image.jpg]
(without an image argument, a sample from Dataset_Split_Zip.zip is used)
"""
import io
import os
import sys
import time
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

from PIL import Image  # noqa: E402

from utils import classification, config, gradcam, llm, segmentation  # noqa: E402


def sample_image_bytes():
    if len(sys.argv) > 1:
        return open(sys.argv[1], "rb").read(), os.path.basename(sys.argv[1])
    z = zipfile.ZipFile(os.path.join(ROOT, "Dataset_Split_Zip.zip"))
    name = next(n for n in z.namelist() if n.startswith("test/Pressure") and not n.endswith("/"))
    return z.read(name), name


def check(name, fn):
    t = time.time()
    try:
        out = fn()
        print(f"[PASS] {name:28s} ({time.time() - t:.2f}s)")
        return out
    except Exception as e:
        print(f"[FAIL] {name:28s} {type(e).__name__}: {e}")
        return None


def main():
    data, name = sample_image_bytes()
    print(f"Image: {name}\n")
    img = Image.open(io.BytesIO(data)).convert("RGB")

    seg = check("1. Segmentation (U-Net)", lambda: segmentation.segment(img) or 1 / 0)
    if seg:
        print(f"       wound area = {seg['area_percent']:.1f}%  found = {seg['found']}")

    x = classification.prepare_input(img, seg)
    cls = check("2. Classification", lambda: classification.classify(x))
    if cls:
        print(f"       {cls['label']} ({cls['confidence']:.1f}%)  input mode = {config.CLASSIFY_INPUT}")

    cam = check("3. Grad-CAM", lambda: gradcam.compute_heatmap(x, cls["index"]))
    if cam is not None:
        print(f"       heatmap shape = {cam.shape}, max = {cam.max():.2f}")

    if llm.is_configured():
        rec = check("4. LLM (Gemini)", lambda: llm.generate_recommendation(img, cls, seg, None) or 1 / 0)
        if rec:
            print(f"       summary: {rec['summary'][:100]}...")
    else:
        print("[SKIP] 4. LLM (Gemini)              GEMINI_API_KEY not set in .env")

    def endpoint():
        import app as flask_app
        client = flask_app.app.test_client()
        assert client.get("/").status_code == 200
        r = client.post("/api/predict", data={"image": (io.BytesIO(data), "x.jpg")},
                        content_type="multipart/form-data")
        assert r.status_code == 200, r.data
        j = r.get_json()
        for key in ("predicted", "probabilities", "mask", "mask_overlay", "gradcam"):
            assert j.get(key) is not None, f"missing {key}"
        return j

    j = check("5. Flask /api/predict", endpoint)
    if j:
        print(f"       predicted = {j['predicted']}, recommendation from LLM = {j['recommendation'] is not None}")


if __name__ == "__main__":
    main()

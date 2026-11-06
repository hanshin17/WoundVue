"""Step 4 — LLM integration (Gemini): turn the classification, Grad-CAM and U-Net results into a structured
multimodal prompt and generate initial-treatment recommendations.

The API key is read from the .env file (GEMINI_API_KEY) via python-dotenv (see utils/config.py).
Uses the official google-genai SDK (the older google-generativeai package is deprecated and its protobuf
requirement conflicts with TensorFlow).
"""
import io
import json
import time

from google.genai import types
from PIL import Image

from . import config

_model = None
_cooldown_until: dict[str, float] = {}  # model_name -> unix timestamp when quota cooldown expires

PROMPT_TEMPLATE = """Anda adalah asisten edukasi kesehatan untuk perawatan luka kulit.
Sebuah sistem AI telah menganalisis citra luka dengan hasil berikut:

- Hasil klasifikasi (model {classifier}): {label} (keyakinan {confidence:.1f}%)
- Tiga kemungkinan teratas: {top3}
- Segmentasi U-Net: {seg_text}
- Grad-CAM: heatmap terlampir menunjukkan area yang menjadi fokus model klasifikasi.

Gambar terlampir secara berurutan: (1) citra asli, (2) binary mask hasil segmentasi U-Net (area luka berwarna putih, latar belakang hitam),
(3) heatmap Grad-CAM.

PENTING — Validasi Citra Ketat (Citra Asli #1):
Periksa citra asli (#1) terlebih dahulu sebelum memberi rekomendasi. Sistem ini HANYA menerima 2 jenis gambar:
  (A) Foto medis close-up LUKA pada kulit manusia (abrasi, luka bakar, luka sayat, laserasi, memar, ulkus diabetik, luka tekan, luka bedah, ulkus vena), ATAU
  (B) Foto makro/close-up PERMUKAAN KULIT manusia yang sehat tanpa luka (di mana permukaan kulit mengisi hampir seluruh frame gambar, tanpa wajah utuh, tanpa pakaian, dan tanpa latar belakang ruangan/studio).

- Jika citra asli BUKAN (A) atau (B) — misalnya: foto potret orang/wajah/selfie/tubuh manusia berpakaian, matahari, planet, hewan, tumbuhan, makanan, layar komputer/HP, benda mati, pemandangan, kartun/ilustrasi, diagram, atau gambar acak apa pun — WAJIB set `"is_valid_skin_or_wound": false` dan `"is_normal_skin": false`.
- Jika citra asli adalah (B) yaitu close-up permukaan kulit sehat tanpa luka, set `"is_valid_skin_or_wound": true` dan `"is_normal_skin": true`.
- Jika citra asli adalah (A) yaitu foto luka pada kulit manusia, set `"is_valid_skin_or_wound": true` dan `"is_normal_skin": false`.

Berdasarkan hasil di atas dan gambar terlampir, berikan informasi penanganan awal dalam Bahasa Indonesia.
Jika keyakinan model rendah atau gambar tampak tidak sesuai dengan label, sebutkan hal tersebut di ringkasan.
Jangan memberikan diagnosis pasti; ini hanya informasi awal.

Jawab HANYA dalam format JSON berikut:
{{
  "is_valid_skin_or_wound": true,
  "is_normal_skin": false,
  "summary": "ringkasan kondisi luka (2-3 kalimat)",
  "steps": ["langkah penanganan awal 1", "langkah 2", "langkah 3", "langkah 4"],
  "warning": "kapan harus segera ke tenaga medis (1-2 kalimat)"
}}"""


def is_configured() -> bool:
    return bool(config.GEMINI_API_KEY)


def _get_model():
    """Gemini client (google-genai SDK, successor of the deprecated google-generativeai package)."""
    global _model
    if _model is None:
        from google import genai

        _model = genai.Client(api_key=config.GEMINI_API_KEY)
    return _model


def build_prompt(cls: dict, seg: dict | None) -> str:
    top3 = ", ".join(f"{p['name']} ({p['prob']:.1f}%)" for p in cls["probabilities"][:3])
    if seg is None:
        seg_text = "tidak tersedia"
    elif not seg["found"]:
        seg_text = "area luka tidak terdeteksi dengan jelas"
    else:
        pct = seg["area_percent"]
        pct_str = f"{pct:.2f}%" if pct < 1.0 else f"{pct:.1f}%"
        seg_text = f"area luka mencakup sekitar {pct_str} dari citra"
    return PROMPT_TEMPLATE.format(
        classifier=config.CLASSIFIER_NAME,
        label=cls["label"],
        confidence=cls["confidence"],
        top3=top3,
        seg_text=seg_text,
    )


def _img_to_part(img: Image.Image) -> types.Part:
    """Encode a 224x224 PIL image as compact JPEG bytes (much smaller & faster to upload than default PNG)."""
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=82, optimize=True)
    return types.Part.from_bytes(data=buf.getvalue(), mime_type="image/jpeg")


def generate_recommendation(original: Image.Image, cls: dict, seg: dict | None,
                            gradcam_img: Image.Image | None) -> dict | None:
    """Returns {"summary", "steps", "warning", "model"} or None if the LLM is not configured / fails."""
    if not is_configured():
        return None

    parts = [
        build_prompt(cls, seg),
        _img_to_part(original.resize((config.IMG_SIZE, config.IMG_SIZE))),
    ]
    if seg is not None:
        parts.append(_img_to_part(seg["overlay_image"]))
    if gradcam_img is not None:
        parts.append(_img_to_part(gradcam_img))

    now = time.time()
    seen = set()
    all_models = [m for m in config.GEMINI_FALLBACK_MODELS if not (m in seen or seen.add(m))]
    # Try models that are not in quota cooldown first, then any cooled-down models as a last resort
    active_models = [m for m in all_models if _cooldown_until.get(m, 0) <= now]
    cooled_models = [m for m in all_models if _cooldown_until.get(m, 0) > now]
    models_to_try = active_models + cooled_models

    gen_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.2,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )

    for model_name in models_to_try:
        try:
            t0 = time.perf_counter()
            response = _get_model().models.generate_content(
                model=model_name,
                contents=parts,
                config=gen_config,
            )
            elapsed = time.perf_counter() - t0
            raw_text = response.text.strip()
            print(f"\n========== RAW TEXT OUTPUT DARI API LLM ({model_name} | {elapsed:.2f}s) ==========")
            print(raw_text)
            print("=================================================================\n")
            data = json.loads(raw_text)
            return {
                "is_valid_skin_or_wound": bool(data.get("is_valid_skin_or_wound", True)),
                "is_normal_skin": bool(data.get("is_normal_skin", False)),
                "summary": str(data.get("summary", "")),
                "steps": [str(s) for s in data.get("steps", [])],
                "warning": str(data.get("warning", "")),
                "model": model_name,
                "raw_text": raw_text,
            }
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                # Skip this model for 10 minutes so subsequent uploads don't wait on a 429 round-trip
                _cooldown_until[model_name] = time.time() + 600
            print(f"[llm] Gemini ({model_name}) error:", err_str[:140])
            continue
    return None

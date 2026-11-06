# WoundVue — Sistem Identifikasi & Klasifikasi Luka pada Kulit

**WoundVue** adalah prototipe aplikasi web berbasis kecerdasan buatan (*Artificial Intelligence*) untuk membantu identifikasi, segmentasi, klasifikasi, interpretasi visual, dan rekomendasi penanganan awal pada luka kulit manusia. Sistem ini dikembangkan sebagai bagian dari penelitian skripsi di **Fakultas Ilmu Komputer, Universitas Klabat**.

---

## Arsitektur Pipeline (4 Tahap Terpadu)

1. **Segmentasi Area Luka (`U-Net`)** — Menghasilkan *binary mask* (`224 × 224` piksel) hitam-putih untuk mengisolasi batas anatomis luka dan menghitung persentase luas area luka.
2. **Klasifikasi Jenis Luka (`EfficientNet` Transfer Learning)** — Mengklasifikasikan citra ke dalam **10 kelas**:
   - `Abrasions`, `Burns`, `Cut`, `Laceration`, `Bruises`, `Diabetic Wounds`, `Normal Skin`, `Pressure Wounds`, `Surgical Wounds`, dan `Venous Wounds`.
3. **Interpretasi Visual (`Grad-CAM` / Explainable AI)** — Menghasilkan peta panas (*heatmap*) yang menunjukkan area fokus utama model klasifikasi saat mengambil keputusan.
4. **Rekomendasi Penanganan Awal (`Gemini 3.5 Flash` Multimodal LLM)** — Memvalidasi citra secara visual dan menyusun ringkasan kondisi, langkah penanganan awal, serta peringatan medis dalam Bahasa Indonesia.

---

## Struktur Folder Proyek

```text
SystemUI/
├── .vscode/
│   ├── launch.json                      # Konfigurasi Run & Debug VS Code
│   └── settings.json                    # Pengaturan interpreter Python (.venv)
├── models/
│   ├── classifier_efficientnet.keras    # Model klasifikasi EfficientNet (10 kelas)
│   └── unet_segmentation.keras          # Model segmentasi U-Net (binary mask)
├── static/
│   ├── css/style.css                    # Styling antarmuka pengguna (UI)
│   ├── images/                          # Logo WoundVue & foto tim pengembang
│   └── js/main.js                       # Logika front-end & komunikasi API
├── templates/
│   └── index.html                       # Halaman Utama, Analisis, dan Kontak
├── tests/
│   ├── evaluate_models.py               # Skrip evaluasi akurasi model pada test set
│   └── test_pipeline.py                 # Skrip pengujian fungsional end-to-end
├── utils/
│   ├── config.py                        # Konfigurasi path, kelas, dan environment
│   ├── segmentation.py                  # Modul inferensi U-Net
│   ├── classification.py                # Modul inferensi EfficientNet
│   ├── gradcam.py                       # Modul komputasi heatmap Grad-CAM
│   ├── llm.py                           # Modul integrasi API Gemini multimodal
│   └── image_utils.py                   # Utilitas pemrosesan & validasi citra
├── .env.example                         # Contoh template konfigurasi API Key
├── app.py                               # Server utama Flask (http://127.0.0.1:5000)
└── requirements.txt                     # Daftar pustaka Python yang dibutuhkan
```

---

## Cara Menjalankan Sistem di Komputer Lain (Clone dari GitHub)

### 1. Clone Repository
```powershell
git clone <URL_REPOSITORY_GITHUB_ANDA>
cd SystemUI
```

### 2. Buat Virtual Environment & Install Library
```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

### 3. Pastikan File Model `.keras` Tersedia di Folder `models/`
- Kedua model (`models/classifier_efficientnet.keras` dan `models/unet_segmentation.keras`) sudah dilacak langsung di dalam repository ini menggunakan **Git LFS** (`.gitattributes`), sehingga otomatis terunduh saat melakukan `git clone`.
- *(Jika komputer tujuan belum menginstal Git LFS, jalankan `git lfs pull` setelah menginstal Git LFS).*

### 4. Konfigurasi `GEMINI_API_KEY` (File `.env`)
Salin file `.env.example` menjadi `.env`:
```powershell
copy .env.example .env
```
Buka file `.env` dan isi `GEMINI_API_KEY` dengan kunci API Google AI Studio Anda:
```env
GEMINI_API_KEY=masukkan_api_key_gemini_anda_di_sini
GEMINI_MODEL=gemini-3.5-flash
CLASSIFY_INPUT=original
```

### 5. Jalankan Aplikasi Flask
```powershell
.\.venv\Scripts\python app.py
```
Kemudian buka browser dan akses: **`http://127.0.0.1:5000`**

---

## Tim Pengembang
- **Bhakti, Johan** (`johansatya93@gmail.com`)
- **Runtukahu, Kyran** (`kyranruntukahu38@gmail.com`)
- **Masengi, Mitchelly** (`mitchellymasengi@gmail.com`)

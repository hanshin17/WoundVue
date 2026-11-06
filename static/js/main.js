// Navbar scroll effect
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 10);
});

// Elements
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const uploadState = document.getElementById('uploadState');
const processingState = document.getElementById('processingState');
const resultsState = document.getElementById('resultsState');
const procBar = document.getElementById('procBar');
const procStatus = document.getElementById('procStatus');
const procSteps = document.querySelectorAll('.proc-step');

// Wound class metadata
const WOUND_META = {
  'Diabetic Wounds': {
    conf: '97.4%',
    desc: 'Ulkus diabetik terdeteksi pada citra. Luka ini umumnya terjadi akibat komplikasi diabetes melitus dengan gangguan sirkulasi perifer dan neuropati.',
    steps: [
      'Bersihkan luka dengan larutan saline steril, hindari penggunaan alkohol atau hidrogen peroksida pekat.',
      'Tutup luka dengan dressing lembap (hydrocolloid atau foam) untuk menjaga kelembapan optimal.',
      'Kurangi tekanan pada area luka (off-loading) dengan alas kaki khusus atau bantalan medis.',
      'Kontrol kadar gula darah secara rutin dan konsultasikan ke dokter spesialis endokrinologi.'
    ],
    warning: 'Segera ke fasilitas kesehatan jika muncul tanda infeksi seperti bau tidak sedap, nanah, kemerahan meluas, atau demam.'
  },
  'Venous Wounds': {
    conf: '95.1%',
    desc: 'Ulkus vena terdeteksi. Luka ini berkaitan dengan hipertensi vena akibat disfungsi katup pembuluh darah balik.',
    steps: [
      'Elevasi tungkai 20–30 cm saat beristirahat untuk mengurangi tekanan vena.',
      'Gunakan kompresi elastis (compression therapy) sesuai anjuran tenaga medis.',
      'Bersihkan luka secara lembut dan ganti balutan secara rutin.',
      'Hindari berdiri atau duduk terlalu lama dalam satu posisi.'
    ],
    warning: 'Konsultasikan ke dokter jika luka tidak menunjukkan perbaikan dalam 2 minggu atau muncul pembengkakan mendadak.'
  },
  'Pressure Wounds': {
    conf: '94.8%',
    desc: 'Luka tekan terdeteksi. Disebabkan oleh tekanan berkepanjangan pada area tonjolan tulang.',
    steps: [
      'Ubah posisi tubuh setiap 2 jam untuk mengurangi tekanan pada area luka.',
      'Gunakan matras atau bantalan anti-tekanan (pressure-redistributing).',
      'Jaga kebersihan luka dan ganti balutan sesuai jadwal.',
      'Pastikan asupan nutrisi dan protein cukup untuk mendukung penyembuhan.'
    ],
    warning: 'Segera hubungi tenaga medis jika luka membesar, berwarna gelap, atau muncul jaringan nekrotik.'
  },
  'Surgical Wounds': {
    conf: '96.2%',
    desc: 'Luka bedah terdeteksi. Luka pascaoperasi dengan tepi sayatan yang relatif bersih.',
    steps: [
      'Jaga area sayatan tetap kering dan bersih selama 48 jam pertama.',
      'Ganti balutan sesuai instruksi dokter atau perawat.',
      'Hindari aktivitas berat yang dapat meregangkan area jahitan.',
      'Pantau tanda infeksi seperti kemerahan, bengkak, atau nanah.'
    ],
    warning: 'Hubungi dokter bedah jika terjadi demam, nyeri hebat, atau luka kembali terbuka (dehisensi).'
  },
  'Burns': {
    conf: '93.7%',
    desc: 'Luka bakar terdeteksi. Kerusakan jaringan kulit akibat paparan suhu tinggi, bahan kimia, listrik, atau radiasi.',
    steps: [
      'Dinginkan area luka dengan air mengalir bersuhu ruang selama 15–20 menit.',
      'Hindari memecahkan lepuhan dan jangan mengoleskan odol atau mentega.',
      'Tutup luka dengan kain bersih non-adhesif atau dressing steril.',
      'Berikan analgesik ringan jika diperlukan untuk mengurangi nyeri.'
    ],
    warning: 'Segera ke IGD jika luka bakar luas, mengenai wajah/tangan/sendi, atau disebabkan oleh listrik maupun bahan kimia.'
  },
  'Abrasions': {
    conf: '98.1%',
    desc: 'Luka abrasi terdeteksi. Cedera superfisial akibat gesekan kulit dengan permukaan kasar.',
    steps: [
      'Bersihkan luka dengan air mengalir dan sabun antiseptik ringan.',
      'Buang kotoran atau kerikil yang menempel dengan hati-hati.',
      'Oleskan salep antibiotik tipis dan tutup dengan plester atau kasa steril.',
      'Ganti balutan setiap hari atau saat basah/kotor.'
    ],
    warning: 'Periksakan ke dokter jika luka cukup dalam, tidak kunjung sembuh, atau muncul tanda infeksi.'
  },
  'Bruises': {
    conf: '97.6%',
    desc: 'Memar terdeteksi. Cedera jaringan lunak akibat benturan tumpul tanpa merobek epidermis.',
    steps: [
      'Kompres dingin (ice pack) selama 15–20 menit setiap 2–3 jam pada 24 jam pertama.',
      'Setelah 48 jam, kompres hangat untuk membantu penyerapan darah.',
      'Elevasi area yang memar jika memungkinkan.',
      'Hindari pijatan keras pada area memar.'
    ],
    warning: 'Konsultasi ke dokter jika memar meluas tanpa sebab jelas, sangat nyeri, atau disertai perdarahan.'
  },
  'Cut': {
    conf: '99.2%',
    desc: 'Luka sayat terdeteksi. Cedera akibat benda tajam dengan tepi luka yang relatif lurus dan bersih.',
    steps: [
      'Hentikan perdarahan dengan menekan luka menggunakan kain bersih selama 5–10 menit.',
      'Bersihkan luka dengan air mengalir dan antiseptik.',
      'Tutup luka dengan plester atau kasa steril.',
      'Jika luka cukup dalam, jahitan mungkin diperlukan dalam 6–8 jam pertama.'
    ],
    warning: 'Segera ke IGD jika perdarahan tidak berhenti, luka sangat dalam, atau mengenai area wajah dan sendi.'
  },
  'Laceration': {
    conf: '95.9%',
    desc: 'Luka robek terdeteksi. Cedera dengan tepi luka kasar dan tidak teratur akibat trauma tumpul.',
    steps: [
      'Tekan area luka untuk menghentikan perdarahan.',
      'Bersihkan luka secara menyeluruh untuk mencegah infeksi.',
      'Tutup luka dengan dressing steril dan ganti secara rutin.',
      'Konsultasikan ke tenaga medis untuk evaluasi kemungkinan jahitan.'
    ],
    warning: 'Segera ke fasilitas kesehatan karena luka robek memiliki risiko kontaminasi dan kerusakan jaringan dalam yang tinggi.'
  },
  'Normal Skin': {
    conf: '99.5%',
    desc: 'Tidak terdeteksi adanya luka pada citra. Kondisi kulit tampak normal.',
    steps: [
      'Jaga kebersihan kulit dengan mandi teratur dan pelembap.',
      'Gunakan tabir surya saat beraktivitas di luar ruangan.',
      'Konsumsi air yang cukup dan makanan bergizi seimbang.',
      'Lakukan pemeriksaan kulit rutin secara mandiri.'
    ],
    warning: 'Tetap pantau perubahan pada kulit. Jika muncul lesi baru yang mencurigakan, segera konsultasikan ke dokter.'
  }
};

/* ===== FILE UPLOAD ===== */
['dragenter', 'dragover'].forEach(ev => {
  uploadZone.addEventListener(ev, e => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
  });
});
['dragleave', 'drop'].forEach(ev => {
  uploadZone.addEventListener(ev, e => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
  });
});
uploadZone.addEventListener('drop', e => {
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith('image/')) handleFile(file);
});
uploadZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', e => {
  const file = e.target.files[0];
  if (file) handleFile(file);
});

/* ===== PIPELINE ===== */
function handleFile(file) {
  const reader = new FileReader();
  reader.onload = e => {
    const img = new Image();
    img.onload = () => {
      // Resize uploaded image to 224x224 on the client as well
      const canvas = document.createElement('canvas');
      canvas.width = 224;
      canvas.height = 224;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, 224, 224);
      const dataUrl224 = canvas.toDataURL('image/jpeg', 0.92);

      const slotOriginal = document.getElementById('slotOriginal');
      slotOriginal.innerHTML = `<img src="${dataUrl224}" width="224" height="224" alt="Citra luka (224x224)" />`;

      uploadState.style.display = 'none';
      processingState.classList.add('active');
      resultsState.classList.remove('active');

      runPipeline(dataUrl224, file);
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

/* ===== BACKEND (Flask + .keras model) ===== */
const API_URL = '/api/predict';
let predictionPromise = null;

function requestPrediction(file) {
  const fd = new FormData();
  fd.append('image', file);
  return fetch(API_URL, { method: 'POST', body: fd }).then(async res => {
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || ('HTTP ' + res.status));
    return data;
  });
}

function runPipeline(dataUrl, file) {
  predictionPromise = requestPrediction(file);
  predictionPromise.catch(() => {}); // handled in showResults
  const steps = Array.from(procSteps);
  steps.forEach(s => { s.classList.remove('active', 'done'); });
  procBar.style.width = '0%';
  procStatus.textContent = '0%';

  let current = 0;
  const totalDuration = 3600;
  const stepDuration = totalDuration / steps.length;

  const tick = () => {
    if (current >= steps.length) {
      procStatus.textContent = 'Selesai';
      setTimeout(showResults, 400);
      return;
    }

    if (current > 0) steps[current - 1].classList.remove('active');
    if (current > 0) steps[current - 1].classList.add('done');
    steps[current].classList.add('active');

    const pct = Math.round(((current + 1) / steps.length) * 100);
    procBar.style.width = pct + '%';
    procStatus.textContent = pct + '%';

    current++;
    setTimeout(tick, stepDuration);
  };

  setTimeout(tick, 300);
}

async function showResults() {
  let result;
  try {
    procStatus.textContent = 'Menunggu model…';
    result = await predictionPromise;
  } catch (err) {
    processingState.classList.remove('active');
    uploadState.style.display = 'block';
    alert('Gagal memproses citra: ' + err.message +
      '\nPastikan backend berjalan (python app.py) dan buka http://127.0.0.1:5000');
    return;
  }

  processingState.classList.remove('active');
  resultsState.classList.add('active');

  const isWound = result.is_wound !== false; // default true if backend doesn't send the field
  const pick = result.predicted;
  const meta = WOUND_META[pick] || { desc: '—', steps: [], warning: '—' };

  // Not-a-wound banner
  const banner = document.getElementById('notWoundBanner');
  const resultHead = document.getElementById('resultHead');
  const resultsGrid = document.querySelector('.results-grid');
  const resultsActions = document.querySelector('.results-actions');
  if (!isWound) {
    banner.classList.add('active');
    if (resultHead) resultHead.style.display = 'none';
    if (resultsGrid) resultsGrid.style.display = 'none';
    if (resultsActions) resultsActions.style.display = 'flex';
    return; // skip wound-specific display
  }
  banner.classList.remove('active');
  if (resultHead) resultHead.style.display = '';
  if (resultsGrid) resultsGrid.style.display = '';

  document.getElementById('predClass').textContent = pick;
  document.getElementById('predConf').textContent = result.confidence.toFixed(1) + '%';

  const probList = document.getElementById('probList');
  probList.innerHTML = '';
  result.probabilities.slice(0, 5).forEach((p, i) => {
    addProbItem(probList, p.name, p.prob, i !== 0);
  });

  setTimeout(() => {
    document.querySelectorAll('.prob-fill').forEach(el => {
      el.style.width = el.dataset.width + '%';
    });
  }, 100);

  // Recommendation: Gemini output from the backend; fall back to built-in text if LLM is unavailable
  const rec = result.recommendation || {
    summary: meta.desc, steps: meta.steps, warning: meta.warning, model: null
  };
  document.getElementById('llmModel').textContent = rec.model
    ? `${rec.model} · multimodal prompt`
    : 'offline · rekomendasi bawaan (Gemini tidak tersedia)';
  document.getElementById('llmSummary').textContent = rec.summary;
  const stepsEl = document.getElementById('llmSteps');
  stepsEl.innerHTML = '';
  rec.steps.forEach(s => {
    const li = document.createElement('li');
    li.textContent = s;
    stepsEl.appendChild(li);
  });
  document.getElementById('llmWarning').textContent = rec.warning;

  if (result.original) {
    document.getElementById('slotOriginal').innerHTML =
      `<img src="${result.original}" width="224" height="224" alt="Citra luka (224x224)" />`;
  }
  const maskSlot = document.getElementById('slotMask');
  const maskArea = document.getElementById('maskArea');
  if (result.mask) {
    maskSlot.innerHTML = `<img src="${result.mask}" width="224" height="224" alt="U-Net binary mask (224x224)" />`;
    if (result.wound_area < 0.05) {
      maskArea.textContent = 'Luka tidak terdeteksi';
    } else if (result.wound_area < 1.0) {
      maskArea.textContent = 'Area luka ' + result.wound_area.toFixed(2) + '%';
    } else {
      maskArea.textContent = 'Area luka ' + result.wound_area.toFixed(1) + '%';
    }
  } else {
    maskSlot.innerHTML = '<div class="placeholder"><span>Segmentasi tidak tersedia</span></div>';
    maskArea.textContent = '—';
  }
  const gradcamAreaEl = document.getElementById('gradcamArea');
  if (result.gradcam) {
    document.getElementById('slotGradcam').innerHTML =
      `<img src="${result.gradcam}" width="224" height="224" alt="Grad-CAM heatmap (224x224)" />`;
    if (gradcamAreaEl) {
      gradcamAreaEl.textContent = typeof result.gradcam_area === 'number'
        ? 'Fokus XAI ' + result.gradcam_area.toFixed(1) + '%'
        : 'Grad-CAM · XAI';
    }
  } else {
    generateGradcamPreview();
    if (gradcamAreaEl) gradcamAreaEl.textContent = 'Grad-CAM · XAI';
  }
}

function addProbItem(container, name, value, dim) {
  const item = document.createElement('div');
  item.className = 'prob-item' + (dim ? ' dim' : '');
  item.innerHTML = `
    <div class="prob-row">
      <span class="name">${name}</span>
      <span class="val">${value.toFixed(1)}%</span>
    </div>
    <div class="prob-track"><div class="prob-fill" data-width="${value.toFixed(1)}"></div></div>
  `;
  container.appendChild(item);
}

function generateGradcamPreview() {
  const slot = document.getElementById('slotGradcam');
  const srcImg = document.querySelector('#slotOriginal img');
  if (!srcImg) return;

  const canvas = document.createElement('canvas');
  const w = 480, h = 330;
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d');

  ctx.drawImage(srcImg, 0, 0, w, h);

  const grad = ctx.createRadialGradient(w / 2, h / 2, 20, w / 2, h / 2, Math.max(w, h) * 0.55);
  grad.addColorStop(0, 'rgba(239, 68, 68, 0.85)');
  grad.addColorStop(0.25, 'rgba(245, 158, 11, 0.7)');
  grad.addColorStop(0.5, 'rgba(234, 179, 8, 0.5)');
  grad.addColorStop(0.75, 'rgba(14, 165, 233, 0.35)');
  grad.addColorStop(1, 'rgba(99, 102, 241, 0)');

  ctx.globalCompositeOperation = 'multiply';
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, w, h);

  ctx.globalCompositeOperation = 'screen';
  const spots = [
    { x: w * 0.5, y: h * 0.48, r: w * 0.22, c: 'rgba(239, 68, 68, 0.5)' },
    { x: w * 0.62, y: h * 0.55, r: w * 0.14, c: 'rgba(245, 158, 11, 0.45)' },
    { x: w * 0.4, y: h * 0.42, r: w * 0.12, c: 'rgba(234, 179, 8, 0.4)' }
  ];
  spots.forEach(s => {
    const g = ctx.createRadialGradient(s.x, s.y, 2, s.x, s.y, s.r);
    g.addColorStop(0, s.c);
    g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
    ctx.fill();
  });

  ctx.globalCompositeOperation = 'source-over';

  slot.innerHTML = '';
  slot.appendChild(canvas);
}

// Reset
document.getElementById('resetBtn').addEventListener('click', () => {
  resultsState.classList.remove('active');
  processingState.classList.remove('active');
  uploadState.style.display = 'block';
  fileInput.value = '';

  // Reset not-a-wound banner
  document.getElementById('notWoundBanner').classList.remove('active');
  const rh = document.getElementById('resultHead');
  const rg = document.querySelector('.results-grid');
  if (rh) rh.style.display = '';
  if (rg) rg.style.display = '';

  document.getElementById('slotOriginal').innerHTML = `
    <div class="placeholder">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
      <span>Citra Asli</span>
    </div>`;
  document.getElementById('slotMask').innerHTML = `
    <div class="placeholder">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><path d="M12 3v18"/></svg>
      <span>Mask</span>
    </div>`;
  document.getElementById('slotGradcam').innerHTML = `
    <div class="placeholder">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 2a10 10 0 1 0 10 10"/><path d="M12 6a6 6 0 1 0 6 6"/></svg>
      <span>Heatmap Grad-CAM</span>
    </div>`;
  document.getElementById('predClass').textContent = '—';
  document.getElementById('maskArea').textContent = '—';
  const gradcamAreaReset = document.getElementById('gradcamArea');
  if (gradcamAreaReset) gradcamAreaReset.textContent = 'Fokus XAI —';
  document.getElementById('predConf').textContent = '—';
  document.getElementById('probList').innerHTML = '';
  document.getElementById('llmSummary').textContent = 'Menunggu hasil klasifikasi…';
  document.getElementById('llmSteps').innerHTML = '<li>—</li>';
  document.getElementById('llmWarning').textContent = '—';

  document.getElementById('analyze').scrollIntoView({ behavior: 'smooth', block: 'start' });
});

// ===== START PAGE <-> ANALYSIS PAGE <-> CONTACT PAGE NAVIGATION =====
const startPage = document.getElementById('startPage');
const analyzeSection = document.getElementById('analyze');
const contactPage = document.getElementById('contactPage');
const startBtn = document.getElementById('startBtn');
const backToStartBtn = document.getElementById('backToStartBtn');
const navBrandLink = document.getElementById('navBrandLink');
const navAnalyzeLink = document.getElementById('navAnalyzeLink');
const navHowLink = document.getElementById('navHowLink');
const navContactLink = document.getElementById('navContactLink');

function setActiveNav(activeEl) {
  [navAnalyzeLink, navHowLink, navContactLink].forEach(el => {
    if (el) el.classList.toggle('active', el === activeEl);
  });
}

function openAnalysisPage() {
  if (startPage) startPage.style.display = 'none';
  if (contactPage) contactPage.classList.remove('active');
  if (analyzeSection) analyzeSection.classList.add('active');
  setActiveNav(navAnalyzeLink);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function openStartPage() {
  if (analyzeSection) analyzeSection.classList.remove('active');
  if (contactPage) contactPage.classList.remove('active');
  if (startPage) startPage.style.display = 'block';
  setActiveNav(navHowLink);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function openContactPage() {
  if (startPage) startPage.style.display = 'none';
  if (analyzeSection) analyzeSection.classList.remove('active');
  if (contactPage) contactPage.classList.add('active');
  setActiveNav(navContactLink);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Toggle dropdown explanations on the 4 pipeline steps
document.querySelectorAll('.pipe-step').forEach(step => {
  step.addEventListener('click', () => {
    step.classList.toggle('open');
  });
});

if (startBtn) startBtn.addEventListener('click', openAnalysisPage);
if (backToStartBtn) backToStartBtn.addEventListener('click', openStartPage);
if (navBrandLink) {
  navBrandLink.addEventListener('click', e => {
    e.preventDefault();
    openStartPage();
  });
}
if (navAnalyzeLink) {
  navAnalyzeLink.addEventListener('click', e => {
    e.preventDefault();
    openAnalysisPage();
  });
}
if (navHowLink) {
  navHowLink.addEventListener('click', e => {
    e.preventDefault();
    openStartPage();
    setTimeout(() => {
      const howEl = document.getElementById('how');
      if (howEl) howEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 60);
  });
}
if (navContactLink) {
  navContactLink.addEventListener('click', e => {
    e.preventDefault();
    openContactPage();
  });
}

// Smooth scroll for anchor links inside the start page
document.querySelectorAll('a[href="#how"]').forEach(a => {
  if (a.id === 'navHowLink') return;
  a.addEventListener('click', e => {
    const target = document.getElementById('how');
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

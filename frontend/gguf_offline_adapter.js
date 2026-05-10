/**
 * Krishi-Veda GGUF Offline Adapter
 * 
 * Downloads vedic_model.gguf (469MB Q4_K_M) from HuggingFace CDN once,
 * stores in IndexedDB, and provides offline inference via a simple
 * pattern-matching fallback when WebGPU/WebLLM is unavailable.
 * 
 * Full llama.cpp WASM inference would require ~1GB WASM build — 
 * not practical for Termux. This adapter ensures the model file is
 * available offline and provides a template-based Vedic reasoning
 * engine as fallback on low-end devices.
 * 
 * Usage:
 *   await GGUFOfflineAdapter.downloadModel(onProgress);
 *   const advice = GGUFOfflineAdapter.getOfflineAdvice(sensorData, kernelData);
 */

(function (global) {
  'use strict';

  const MODEL_URL = 'https://huggingface.co/divinesouljoy/VedaRta-0.5B/resolve/main/vedic_model.gguf';
  const DB_NAME = 'krishi-veda-models';
  const DB_VERSION = 1;
  const STORE_NAME = 'models';
  const MODEL_KEY = 'vedic_model_q4km';

  let _modelBlob = null;
  let _downloadProgress = 0;

  /**
   * Download the GGUF model from HuggingFace CDN and store in IndexedDB.
   * Only downloads if not already cached.
   */
  async function downloadModel(onProgress) {
    // Check if already in IndexedDB
    const existing = await getFromIDB(MODEL_KEY);
    if (existing) {
      _modelBlob = existing;
      onProgress && onProgress({ progress: 1, text: 'Model already cached offline ✅', done: true });
      return true;
    }

    onProgress && onProgress({ progress: 0, text: 'Downloading Vedic AI model (469MB)...' });

    try {
      const response = await fetch(MODEL_URL);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const contentLength = response.headers.get('content-length');
      const total = contentLength ? parseInt(contentLength) : 469 * 1024 * 1024;
      let loaded = 0;
      const chunks = [];

      const reader = response.body.getReader();
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        chunks.push(value);
        loaded += value.length;
        const progress = loaded / total;
        const mbLoaded = (loaded / (1024 * 1024)).toFixed(1);
        const mbTotal = (total / (1024 * 1024)).toFixed(1);
        onProgress && onProgress({
          progress,
          text: `Downloading model: ${mbLoaded}MB / ${mbTotal}MB (${(progress * 100).toFixed(0)}%)`
        });
      }

      const blob = new Blob(chunks);
      await saveToIDB(MODEL_KEY, blob);
      _modelBlob = blob;
      onProgress && onProgress({ progress: 1, text: 'Model cached offline ✅', done: true });
      return true;
    } catch (err) {
      onProgress && onProgress({ progress: 0, text: `Download failed: ${err.message} ❌`, error: true });
      return false;
    }
  }

  /**
   * Check if model is cached offline.
   */
  async function isCached() {
    if (_modelBlob) return true;
    const existing = await getFromIDB(MODEL_KEY);
    if (existing) {
      _modelBlob = existing;
      return true;
    }
    return false;
  }

  /**
   * Get model size in MB.
   */
  async function getCachedSizeMB() {
    const blob = _modelBlob || await getFromIDB(MODEL_KEY);
    return blob ? (blob.size / (1024 * 1024)).toFixed(1) : '0';
  }

  /**
   * Offline Vedic advice — template-based reasoning with kernel grounding.
   * When full WASM inference isn't available, this provides structured
   * advice using the Vedic kernel computations + agricultural rules.
   */
  function getOfflineAdvice({ sensor, lang = 'en', kernelData, soilType, paksha }) {
    const kd = kernelData || {};
    const wellness = kd.gunakasamuccaya?.wellness || kd.wellness || 50;
    const deficit = kd.nikhilam?.deficit_ppm || kd.deficit_ppm || 0;
    const liming = kd.paravartya?.liming_kg_ha || kd.liming_kg_ha || 0;
    const yieldIdx = kd.urdhva?.yield_index || kd.yield_index || 50;
    const ahimsa = kd.ahimsa_triggered || kd.ahimsa_stress > 75;
    const anomaly = kd.vilokanam?.anomaly || false;

    const pH = sensor.ph || sensor.pH || 6.5;
    const N = sensor.N || 35;
    const P = sensor.P || 28;
    const K = sensor.K || 40;
    const moisture = sensor.moisture || 50;

    // Generate structured advice in target language
    const advice = generateVedicAdvice({
      wellness, deficit, liming, yieldIdx, ahimsa, anomaly,
      pH, N, P, K, moisture, soilType, paksha, lang
    });

    return {
      advice: advice.text,
      engine: 'gguf_offline_template',
      model: 'divinesouljoy/VedaRta-0.5B-Q4_K_M',
      model_cached_mb: _modelBlob ? (_modelBlob.size / (1024 * 1024)).toFixed(1) : '0',
      inference_seconds: 0.01,
      ahimsa_triggered: ahimsa,
      wellness_score: wellness,
      yield_index: yieldIdx,
      language: advice.lang,
      offline_note: 'Template-based Vedic reasoning. Full AI inference requires WebGPU browser or online mode.'
    };
  }

  /**
   * Template-based Vedic agricultural advice generator.
   * Uses kernel computations to produce structured, practical advice.
   */
  function generateVedicAdvice({ wellness, deficit, liming, yieldIdx, ahimsa, anomaly, pH, N, P, K, moisture, soilType, paksha, lang }) {
    const templates = {
      en: {
        health_status: wellness > 65 ? 'Good' : wellness > 40 ? 'Moderate' : 'Critical',
        critical_warning: ahimsa ? '⚠️ AHIMSA-108: Critical soil stress detected. Only organic inputs allowed.\n' : '',
        nutrient_advice: deficit > 15 ? `Apply balanced NPK to address ${deficit.toFixed(0)} ppm deficit.` : 'Nutrient levels adequate.',
        lime_advice: liming > 100 ? `Apply ${liming.toFixed(0)} kg/ha agricultural lime to correct pH ${pH}.` : 'Soil pH is within acceptable range.',
        moisture_advice: moisture < 30 ? 'Irrigation needed — soil moisture critically low.' : moisture < 50 ? 'Consider light irrigation.' : 'Soil moisture adequate.',
        paksha_advice: paksha === 'waxing' ? 'Shukla Paksha: Ideal for sowing and growth-stage activities.' : 'Krishna Paksha: Best for harvesting and soil preparation.',
        yield_note: yieldIdx > 65 ? 'Yield outlook: Favorable.' : yieldIdx > 40 ? 'Yield outlook: Moderate — monitor closely.' : 'Yield outlook: Low — intervention recommended.',
        anomaly_warning: anomaly ? '⚠️ Anomaly detected in soil readings. Verify sensor data.\n' : '',
        panchagavya: ahimsa ? '→ Panchgavya Protocol: Mix 5L cow dung, 3L cow urine, 2L milk, 2L curd, 500g ghee. Ferment 7 days. Spray 3% solution at 300L/acre.\n→ No chemical fertilizers until wellness > 50.\n' : '',
        organic_tip: 'Tip: Apply vermicompost at 2 tons/acre for long-term soil health.',
      },
      hi: {
        health_status: wellness > 65 ? 'अच्छी' : wellness > 40 ? 'मध्यम' : 'गंभीर',
        critical_warning: ahimsa ? '⚠️ अहिंसा-108: मिट्टी में गंभीर तनाव। केवल जैविक उपचार।\n' : '',
        nutrient_advice: deficit > 15 ? `${deficit.toFixed(0)} ppm की कमी के लिए संतुलित NPK डालें।` : 'पोषक तत्व पर्याप्त हैं।',
        lime_advice: liming > 100 ? `pH ${pH} के लिए ${liming.toFixed(0)} kg/ha चूना डालें।` : 'मिट्टी का pH सही है।',
        moisture_advice: moisture < 30 ? 'सिंचाई जरूरी — नमी बहुत कम।' : moisture < 50 ? 'हल्की सिंचाई करें।' : 'नमी पर्याप्त है।',
        paksha_advice: paksha === 'waxing' ? 'शुक्ल पक्ष: बुवाई के लिए उत्तम।' : 'कृष्ण पक्ष: कटाई के लिए सर्वोत्तम।',
        yield_note: yieldIdx > 65 ? 'उपज: अनुकूल।' : yieldIdx > 40 ? 'उपज: मध्यम — निगरानी रखें।' : 'उपज: कम — हस्तक्षेप जरूरी।',
        anomaly_warning: anomaly ? '⚠️ मिट्टी रीडिंग में विसंगति। सेंसर जांचें।\n' : '',
        panchagavya: ahimsa ? '→ पंचगव्य: 5L गोबर, 3L गोमूत्र, 2L दूध, 2L दही, 500g घी। 7 दिन खमीर। 3% घोल, 300L/एकड़।\n→ रासायनिक खाद न डालें जब तक वेलनेस > 50।\n' : '',
        organic_tip: 'सुझाव: 2 टन/एकड़ वर्मीकम्पोस्ट डालें।',
      }
    };

    const t = templates[lang] || templates['en'];

    const text = [
      `[Krishi-Veda Offline | ${t.health_status}]`,
      `Wellness: ${wellness.toFixed(0)}/100 | Yield Index: ${yieldIdx.toFixed(0)}/100`,
      '',
      t.anomaly_warning,
      t.critical_warning,
      `🌱 ${t.nutrient_advice}`,
      `🪨 ${t.lime_advice}`,
      `💧 ${t.moisture_advice}`,
      `🌙 ${t.paksha_advice}`,
      `📊 ${t.yield_note}`,
      t.panchagavya ? `\n${t.panchagavya}` : '',
      `\n🌿 ${t.organic_tip}`,
    ].filter(Boolean).join('\n');

    return { text, lang };
  }

  // ── IndexedDB helpers ──────────────────────────────────────────────────
  function openDB() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open(DB_NAME, DB_VERSION);
      req.onupgradeneeded = (e) => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          db.createObjectStore(STORE_NAME);
        }
      };
      req.onsuccess = (e) => resolve(e.target.result);
      req.onerror = (e) => reject(e.target.error);
    });
  }

  async function getFromIDB(key) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, 'readonly');
      const store = tx.objectStore(STORE_NAME);
      const req = store.get(key);
      req.onsuccess = () => resolve(req.result || null);
      req.onerror = () => reject(req.error);
    });
  }

  async function saveToIDB(key, blob) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, 'readwrite');
      const store = tx.objectStore(STORE_NAME);
      store.put(blob, key);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  }

  global.GGUFOfflineAdapter = {
    downloadModel,
    isCached,
    getCachedSizeMB,
    getOfflineAdvice,
    MODEL_URL,
  };
})(window);

/**
 * Krishi-Veda WebLLM Adapter
 *
 * Loads Qwen2.5-0.5B-Instruct (4-bit MLC quantized) entirely in the browser
 * using WebGPU via the @mlc-ai/web-llm library.
 *
 * The Vedic kernel ground-truth (from VedicWASM) is injected into every prompt
 * so the browser LLM cannot contradict the verified kernel outputs — matching
 * the server-side Ahimsa-108 grounding architecture.
 *
 * Usage:
 *   await WebLLMAdapter.load(onProgress);
 *   const advice = await WebLLMAdapter.getAdvice(sensorData);
 */

(function (global) {
  'use strict';

  // Qwen2.5-0.5B-Instruct in MLC 4-bit format (q4f16_1)
  // ~320 MB download, cached in browser cache after first load
  const MODEL_ID = 'Qwen2.5-0.5B-Instruct-q4f16_1-MLC';
  const CDN      = 'https://esm.run/@mlc-ai/web-llm';

  let _engine      = null;
  let _loading     = false;
  let _loaded      = false;
  let _loadError   = null;

  /**
   * Check if WebGPU is available in this browser.
   */
  function isWebGPUSupported() {
    return typeof navigator !== 'undefined' && Boolean(navigator.gpu);
  }

  /**
   * Load the WebLLM engine.
   * @param {function} onProgress  — called with { progress: 0-1, text: string }
   * @returns {Promise<boolean>}   — true if loaded, false if unsupported/failed
   */
  async function load(onProgress) {
    if (_loaded)   return true;
    if (_loading)  return new Promise((res) => { _onLoadResolvers.push(res); });
    if (_loadError) return false;

    if (!isWebGPUSupported()) {
      _loadError = 'WebGPU not supported in this browser. Try Chrome 113+ on a GPU-enabled device.';
      onProgress && onProgress({ progress: 0, text: _loadError, error: true });
      return false;
    }

    _loading = true;

    try {
      onProgress && onProgress({ progress: 0.01, text: 'Loading WebLLM library…' });

      const webllm = await import(CDN);
      const engine = new webllm.MLCEngine();

      await engine.reload(MODEL_ID, {
        initProgressCallback: (info) => {
          onProgress && onProgress({
            progress: info.progress || 0,
            text: info.text || 'Loading model…',
          });
        },
      });

      _engine = engine;
      _loaded = true;
      _loading = false;
      onProgress && onProgress({ progress: 1, text: '✅ Browser LLM ready', done: true });
      _onLoadResolvers.forEach((res) => res(true));
      return true;
    } catch (err) {
      _loadError = err.message;
      _loading   = false;
      onProgress && onProgress({ progress: 0, text: `❌ ${err.message}`, error: true });
      _onLoadResolvers.forEach((res) => res(false));
      return false;
    }
  }

  const _onLoadResolvers = [];

  /**
   * Generate Vedic agricultural advice in the browser.
   * Vedic kernel ground truth is injected before LLM inference.
   *
   * @param {object} params
   *   sensor: { ph, N, P, K, moisture, om }
   *   lang: 'en' | 'hi' | 'bn' | 'as'
   *   kernelData: result of VedicWASM.runAllSutras(sensor)
   */
  async function getAdvice({ sensor, lang = 'en', kernelData }) {
    if (!_loaded || !_engine) {
      return { error: 'Model not loaded', advice: null };
    }

    const kd = kernelData || (global.VedicWASM ? global.VedicWASM.runAllSutras(sensor) : null);

    const groundTruth = kd
      ? `[VEDIC KERNEL GROUND TRUTH — do not contradict]
Soil Wellness (Gunakasamuccaya): ${kd.gunakasamuccaya?.wellness ?? '—'}/100
NPK Deficit (Nikhilam): ${kd.nikhilam?.deficit_ppm ?? '—'} ppm below ideal
Liming Need (Paravartya): ${kd.paravartya?.liming_kg_ha ?? '—'} kg/ha
Yield Index (Urdhva-Tiryak): ${kd.urdhva?.yield_index ?? '—'}/100
Ahimsa-108 Stress Code: ${kd.ahimsa_stress ?? '—'}
Anomaly Detected (Vilokanam): ${kd.vilokanam?.anomaly ? 'YES ⚠️' : 'No'}
Ahimsa Protocol Triggered: ${kd.ahimsa_triggered ? 'YES — prescribe organic only' : 'No'}`
      : '[Kernel data unavailable — use general Vedic principles]';

    const langInstruction = {
      hi: 'Respond in simple Hindi (हिंदी).',
      bn: 'Respond in simple Bengali (বাংলা).',
      as: 'Respond in simple Assamese (অসমীয়া).',
      en: 'Respond in simple English.',
    }[lang] || 'Respond in simple English.';

    const prompt = `You are Krishi-Veda, a Vedic agricultural advisor for rural Indian farmers.
${groundTruth}

Sensor readings: pH=${sensor.ph}, N=${sensor.N} ppm, P=${sensor.P} ppm, K=${sensor.K} ppm, Moisture=${sensor.moisture}%, Organic Matter=${sensor.om}%.

${langInstruction} Give a practical 3-point farming recommendation based strictly on the kernel data above. Keep each point to one sentence. Do not suggest any chemical inputs if Ahimsa Protocol is triggered.`;

    const start = Date.now();
    const reply = await _engine.chat.completions.create({
      messages: [{ role: 'user', content: prompt }],
      max_tokens: 220,
      temperature: 0.4,
    });

    const text    = reply.choices[0]?.message?.content || '';
    const elapsed = ((Date.now() - start) / 1000).toFixed(2);

    return {
      advice:           text.trim(),
      engine:           'webllm_browser',
      model:            MODEL_ID,
      inference_seconds: parseFloat(elapsed),
      ahimsa_triggered: kd?.ahimsa_triggered || false,
      vedic_grounding:  kd || {},
    };
  }

  global.WebLLMAdapter = {
    load,
    getAdvice,
    isReady:           () => _loaded,
    isWebGPUSupported,
    getError:          () => _loadError,
    MODEL_ID,
  };
})(window);

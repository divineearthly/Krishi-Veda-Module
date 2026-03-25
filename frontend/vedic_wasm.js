/**
 * Krishi-Veda WASM Bridge
 *
 * Loads the emscripten-compiled vedic_kernels.wasm when available.
 * Falls back to an identical pure-JavaScript implementation so the app
 * works in development (where emscripten hasn't compiled yet) and in
 * browsers without WASM support.
 *
 * Usage (after window.VedicWASM.ready resolves):
 *   const result = VedicWASM.anurupyena_scale(35, 40, 0.1);
 *   const plan   = VedicWASM.runAllSutras({ ph, N, P, K, moisture, om });
 */

(function (global) {
  'use strict';

  // ── Pure-JS fallback: mirrors vedic_kernels.cpp exactly ─────────────────

  const JS = {
    anurupyena_scale(observed, ideal_ref, tolerance = 0.05) {
      if (ideal_ref <= 0) return 1.0;
      const ratio = observed / ideal_ref;
      if (Math.abs(ratio - 1.0) <= tolerance) return 1.0;
      return Math.max(0.1, Math.min(2.0, 1.0 - 0.5 * (ratio - 1.0)));
    },

    nikhilam_deficit(n_val, p_val, k_val) {
      const BASE = 40.0;
      const nc = BASE - Math.min(n_val, BASE);
      const pc = BASE - Math.min(p_val, BASE);
      const kc = BASE - Math.min(k_val, BASE);
      return (nc + pc + kc) / 3.0;
    },

    paravartya_ph_inversion(ph, target_ph = 6.5) {
      return -(ph - target_ph) * 250.0;
    },

    ekadhikena_next_stage(current_index, growth_stage = 0) {
      const increments = [1.0, 1.618, 2.618, 4.236, 6.854, 11.09, 17.94, 29.03];
      const idx = Math.min(growth_stage, 7);
      return current_index + increments[idx];
    },

    urdhva_yield_score(soil_health, water_index, solar_index, temp_factor) {
      const cross1    = soil_health * water_index;
      const cross2    = solar_index * temp_factor;
      const vertical  = soil_health * solar_index + water_index * temp_factor;
      const score     = (cross1 + cross2 + vertical) / 30000.0 * 100.0;
      return Math.min(100.0, Math.max(0.0, score));
    },

    vilokanam_anomaly(values, threshold_sigma = 2.5) {
      if (values.length < 2) return 0;
      const mean   = values.reduce((a, b) => a + b, 0) / values.length;
      const variance = values.reduce((a, b) => a + (b - mean) ** 2, 0) / values.length;
      const stddev = Math.sqrt(variance);
      if (stddev === 0) return 0;
      return Math.abs(values[values.length - 1] - mean) > threshold_sigma * stddev ? 1 : 0;
    },

    gunakasamuccaya_wellness(ph_score, npk_score, moisture_score, om_score) {
      const product = ph_score * npk_score * moisture_score * om_score;
      const geo_mean = Math.pow(Math.max(product, 0.0001), 0.25);
      return Math.min(100.0, geo_mean);
    },

    shunyam_stress_balance(stress_index, amendment_potency) {
      const residual = stress_index - amendment_potency;
      return Math.abs(residual) < 1.0 ? 0.0 : residual;
    },

    ahimsa_108_stress_code(nikhilam_deficit, paravartya_deviation, vilokanam_flag, wellness) {
      const base              = (nikhilam_deficit / 40.0) * 60.0;
      const ph_penalty        = Math.abs(paravartya_deviation) * 2.0;
      const anomaly_penalty   = vilokanam_flag * 20.0;
      const wellness_penalty  = (100.0 - wellness) * 0.3;
      return base + ph_penalty + anomaly_penalty + wellness_penalty;
    },

    /**
     * Run all 8 sutras from raw sensor readings and return full computation.
     * sensor: { ph, N, P, K, moisture, om, growth_stage }
     */
    runAllSutras(sensor) {
      const { ph = 6.5, N = 35, P = 28, K = 40, moisture = 50, om = 2.0, growth_stage = 0 } = sensor;

      const ph_score     = Math.max(0, Math.min(100, (1 - Math.abs(ph - 6.5) / 3.5) * 100));
      const npk_avg      = (N + P + K) / 3.0;
      const npk_score    = Math.min(100, (npk_avg / 40.0) * 100);
      const moisture_score = Math.min(100, moisture);
      const om_score     = Math.min(100, om * 25);

      const anurupyena     = JS.anurupyena_scale(npk_avg, 40, 0.1);
      const nikhilam       = JS.nikhilam_deficit(N, P, K);
      const paravartya     = JS.paravartya_ph_inversion(ph, 6.5);
      const ekadhikena     = JS.ekadhikena_next_stage(npk_avg, growth_stage);
      const urdhva         = JS.urdhva_yield_score(ph_score, moisture_score, 70, 75);
      const vilokanam      = JS.vilokanam_anomaly([N, P, K, ph * 10]);
      const gunakasamuccaya = JS.gunakasamuccaya_wellness(ph_score, npk_score, moisture_score, om_score);
      const shunyam        = JS.shunyam_stress_balance(nikhilam, om_score * 0.3);
      const ahimsa         = JS.ahimsa_108_stress_code(nikhilam, Math.abs(paravartya), vilokanam, gunakasamuccaya);

      return {
        engine: 'wasm_js_fallback',
        anurupyena:       { scale_factor: +anurupyena.toFixed(3) },
        nikhilam:         { deficit_ppm: +nikhilam.toFixed(2) },
        paravartya:       { liming_kg_ha: +paravartya.toFixed(1) },
        ekadhikena:       { next_milestone: +ekadhikena.toFixed(2) },
        urdhva:           { yield_index: +urdhva.toFixed(1) },
        vilokanam:        { anomaly: vilokanam === 1 },
        gunakasamuccaya:  { wellness: +gunakasamuccaya.toFixed(1) },
        shunyam:          { residual_stress: +shunyam.toFixed(2), balanced: Math.abs(shunyam) < 1 },
        ahimsa_stress:    +ahimsa.toFixed(1),
        ahimsa_triggered: ahimsa >= 75,
      };
    },
  };

  // ── WASM Loader ──────────────────────────────────────────────────────────
  let _api = JS;   // default: JS fallback

  const readyPromise = (async () => {
    // Only attempt WASM load if the glue script exists (production Docker build)
    try {
      // The emscripten build outputs vedic_kernels.js + vedic_kernels.wasm
      // served at /static/vedic_kernels.js from the frontend/ directory
      await new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = '/static/vedic_kernels.js';
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
      });

      // Wait for emscripten module to be ready
      await new Promise((resolve) => {
        if (typeof Module !== 'undefined' && Module.onRuntimeInitialized) {
          Module.onRuntimeInitialized = resolve;
        } else {
          resolve();
        }
      });

      if (typeof Module !== 'undefined') {
        // Wrap emscripten cwrap calls
        const w = {
          anurupyena_scale:       Module.cwrap('anurupyena_scale',       'number', ['number','number','number']),
          nikhilam_deficit:       Module.cwrap('nikhilam_deficit',       'number', ['number','number','number']),
          paravartya_ph_inversion:Module.cwrap('paravartya_ph_inversion','number', ['number','number']),
          ekadhikena_next_stage:  Module.cwrap('ekadhikena_next_stage',  'number', ['number','number']),
          urdhva_yield_score:     Module.cwrap('urdhva_yield_score',     'number', ['number','number','number','number']),
          gunakasamuccaya_wellness:Module.cwrap('gunakasamuccaya_wellness','number',['number','number','number','number']),
          shunyam_stress_balance: Module.cwrap('shunyam_stress_balance', 'number', ['number','number']),
          ahimsa_108_stress_code: Module.cwrap('ahimsa_108_stress_code', 'number', ['number','number','number','number']),
        };
        // vilokanam needs array pointer — keep JS for it
        _api = {
          ...JS,           // keeps runAllSutras and vilokanam (array)
          ...w,            // override scalar functions with WASM versions
          runAllSutras: JS.runAllSutras,  // keep JS composite function
          _wasm: true,
        };
        console.log('[VedicWASM] ✅ Native WASM kernels loaded');
      }
    } catch {
      console.log('[VedicWASM] ℹ️  WASM not found — using pure-JS Vedic kernels (identical math)');
    }
    return _api;
  })();

  global.VedicWASM = {
    ready: readyPromise,
    // Synchronous passthrough (safe after await VedicWASM.ready)
    anurupyena_scale:        (...a) => _api.anurupyena_scale(...a),
    nikhilam_deficit:        (...a) => _api.nikhilam_deficit(...a),
    paravartya_ph_inversion: (...a) => _api.paravartya_ph_inversion(...a),
    ekadhikena_next_stage:   (...a) => _api.ekadhikena_next_stage(...a),
    urdhva_yield_score:      (...a) => _api.urdhva_yield_score(...a),
    vilokanam_anomaly:       (...a) => _api.vilokanam_anomaly(...a),
    gunakasamuccaya_wellness:(...a) => _api.gunakasamuccaya_wellness(...a),
    shunyam_stress_balance:  (...a) => _api.shunyam_stress_balance(...a),
    ahimsa_108_stress_code:  (...a) => _api.ahimsa_108_stress_code(...a),
    runAllSutras:            (...a) => _api.runAllSutras(...a),
    isWasm:                  () => Boolean(_api._wasm),
  };
})(window);

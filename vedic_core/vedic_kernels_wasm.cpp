/**
 * Krishi-Veda: 8 Krishi-Sutras — Emscripten / WebAssembly build
 *
 * This file is identical in math to vedic_kernels.cpp but adds
 * EMSCRIPTEN_KEEPALIVE so every function is exported to JavaScript.
 *
 * Compile with:
 *   emcc -Os -s WASM=1 \
 *        -s EXPORTED_RUNTIME_METHODS='["cwrap","ccall","FS"]' \
 *        -s EXPORTED_FUNCTIONS='["_anurupyena_scale","_nikhilam_deficit",\
 *           "_paravartya_ph_inversion","_ekadhikena_next_stage",\
 *           "_urdhva_yield_score","_vilokanam_anomaly",\
 *           "_gunakasamuccaya_wellness","_shunyam_stress_balance",\
 *           "_ahimsa_108_stress_code","_malloc","_free"]' \
 *        -s MODULARIZE=0 \
 *        -s ENVIRONMENT='web,worker' \
 *        vedic_core/vedic_kernels_wasm.cpp \
 *        -o frontend/vedic_kernels.js
 *
 * Output: frontend/vedic_kernels.js + frontend/vedic_kernels.wasm
 */

#include <cmath>
#include <cstring>
#include <algorithm>
#include <emscripten.h>

#define EXPORT EMSCRIPTEN_KEEPALIVE

extern "C" {

/** 1. ANURUPYENA — Proportional NPK scaling */
EXPORT double anurupyena_scale(double observed, double ideal_ref, double tolerance) {
    if (ideal_ref <= 0.0) return 1.0;
    double ratio = observed / ideal_ref;
    if (std::fabs(ratio - 1.0) <= tolerance) return 1.0;
    return std::max(0.1, std::min(2.0, 1.0 - 0.5 * (ratio - 1.0)));
}

/** 2. NIKHILAM — Complement-based deficit (all from base 40 ppm) */
EXPORT double nikhilam_deficit(double n_val, double p_val, double k_val) {
    const double BASE = 40.0;
    double n_comp = BASE - std::min(n_val, BASE);
    double p_comp = BASE - std::min(p_val, BASE);
    double k_comp = BASE - std::min(k_val, BASE);
    return (n_comp + p_comp + k_comp) / 3.0;
}

/** 3. PARAVARTYA — pH inversion → liming/acidification kg/ha */
EXPORT double paravartya_ph_inversion(double ph, double target_ph) {
    return -(ph - target_ph) * 250.0;
}

/** 4. EKADHIKENA — Next growth stage milestone (golden-ratio increments) */
EXPORT double ekadhikena_next_stage(double current_index, int growth_stage) {
    double increments[] = {1.0, 1.618, 2.618, 4.236, 6.854, 11.09, 17.94, 29.03};
    int idx = std::min(growth_stage, 7);
    return current_index + increments[idx];
}

/** 5. URDHVA-TIRYAK — Cross-multiply yield matrix */
EXPORT double urdhva_yield_score(
    double soil_health, double water_index,
    double solar_index, double temp_factor
) {
    double cross1   = soil_health * water_index;
    double cross2   = solar_index * temp_factor;
    double vertical = soil_health * solar_index + water_index * temp_factor;
    double score    = (cross1 + cross2 + vertical) / 30000.0 * 100.0;
    return std::min(100.0, std::max(0.0, score));
}

/** 6. VILOKANAM — Sensor anomaly detection (array pointer, use from JS via ccall) */
EXPORT int vilokanam_anomaly(double* values, int count, double threshold_sigma) {
    if (count < 2) return 0;
    double sum = 0.0;
    for (int i = 0; i < count; i++) sum += values[i];
    double mean = sum / count;
    double var  = 0.0;
    for (int i = 0; i < count; i++) var += (values[i] - mean) * (values[i] - mean);
    double stddev = std::sqrt(var / count);
    if (stddev == 0.0) return 0;
    return (std::fabs(values[count - 1] - mean) > threshold_sigma * stddev) ? 1 : 0;
}

/** 7. GUNAKASAMUCCAYA — Geometric mean wellness index */
EXPORT double gunakasamuccaya_wellness(
    double ph_score, double npk_score,
    double moisture_score, double organic_matter_score
) {
    double product  = ph_score * npk_score * moisture_score * organic_matter_score;
    double geo_mean = std::pow(std::max(product, 0.0001), 0.25);
    return std::min(100.0, geo_mean);
}

/** 8. SHUNYAM — Residual stress after organic amendment */
EXPORT double shunyam_stress_balance(double stress_index, double amendment_potency) {
    double residual = stress_index - amendment_potency;
    return (std::fabs(residual) < 1.0) ? 0.0 : residual;
}

/** AHIMSA-108 PROTOCOL — Composite stress code (≥ 75 triggers organic pivot) */
EXPORT double ahimsa_108_stress_code(
    double nikhilam_deficit_val,
    double paravartya_deviation,
    int    vilokanam_flag,
    double gunakasamuccaya_wellness_val
) {
    double base             = (nikhilam_deficit_val / 40.0) * 60.0;
    double ph_penalty       = std::fabs(paravartya_deviation) * 2.0;
    double anomaly_penalty  = vilokanam_flag * 20.0;
    double wellness_penalty = (100.0 - gunakasamuccaya_wellness_val) * 0.3;
    return base + ph_penalty + anomaly_penalty + wellness_penalty;
}

} // extern "C"

/**
 * Krishi-Veda: 8 Krishi-Sutras
 * Compiled as a lightweight shared library for agricultural computation.
 * Each sutra maps an ancient Vedic mathematical principle to a farming metric.
 */
#include <cmath>
#include <cstring>
#include <algorithm>

extern "C" {

/**
 * 1. ANURUPYENA (Proportionality)
 * Scales soil nutrient scores proportionally against an ideal reference.
 * Returns a correction factor in [0.0, 2.0] where 1.0 = perfect balance.
 */
double anurupyena_scale(double observed, double ideal_ref, double tolerance) {
    if (ideal_ref <= 0.0) return 1.0;
    double ratio = observed / ideal_ref;
    if (std::fabs(ratio - 1.0) <= tolerance) return 1.0;
    // Smooth penalty using proportional convergence
    return std::max(0.1, std::min(2.0, 1.0 - 0.5 * (ratio - 1.0)));
}

/**
 * 2. NIKHILAM (All from 9, last from 10 — complement)
 * Computes soil deficit index: how far nutrients are from their 100-base ideal.
 * Returns a deficit score. Lower = better.
 */
double nikhilam_deficit(double n_val, double p_val, double k_val) {
    // Each nutrient ideally near 40 ppm (base 40 for agricultural NPK)
    const double BASE = 40.0;
    double n_comp = BASE - std::min(n_val, BASE);
    double p_comp = BASE - std::min(p_val, BASE);
    double k_comp = BASE - std::min(k_val, BASE);
    return (n_comp + p_comp + k_comp) / 3.0;
}

/**
 * 3. PARAVARTYA (Transpose and Adjust)
 * Inverts an adverse pH deviation into a liming/acidification recommendation.
 * Returns liming index: positive = add lime, negative = add sulfur, 0 = balanced.
 */
double paravartya_ph_inversion(double ph, double target_ph) {
    double deviation = ph - target_ph;
    // Invert and scale: 1 unit pH dev needs ~500 kg/ha amendment (simplified)
    return -deviation * 250.0;
}

/**
 * 4. EKADHIKENA (One More Than Previous)
 * Computes the next optimal growth stage threshold.
 * Given current biomass index, predicts next milestone using Vedic increment.
 */
double ekadhikena_next_stage(double current_index, int growth_stage) {
    // Fibonacci-like progression for crop growth stages (0-indexed: 0=seed,1=sprout,...)
    double base_increments[] = {1.0, 1.618, 2.618, 4.236, 6.854, 11.09, 17.94, 29.03};
    int idx = std::min(growth_stage, 7);
    return current_index + base_increments[idx];
}

/**
 * 5. URDHVA-TIRYAK (Crosswise and Vertical Multiplication)
 * Computes weighted crop yield score from multiple interaction factors.
 * Returns an estimated yield index.
 */
double urdhva_yield_score(
    double soil_health,   // 0-100
    double water_index,   // 0-100
    double solar_index,   // 0-100
    double temp_factor    // 0-100
) {
    // Cross-multiply pairs then sum vertically (Urdhva pattern)
    double cross1 = soil_health * water_index;
    double cross2 = solar_index * temp_factor;
    double vertical = soil_health * solar_index + water_index * temp_factor;
    double score = (cross1 + cross2 + vertical) / 30000.0 * 100.0;
    return std::min(100.0, std::max(0.0, score));
}

/**
 * 6. VILOKANAM (By Mere Observation / Inspection)
 * Detects anomalies in sensor readings using inter-quartile deviation.
 * Returns 1 if anomaly detected, 0 otherwise.
 */
int vilokanam_anomaly(double* values, int count, double threshold_sigma) {
    if (count < 2) return 0;
    double sum = 0.0;
    for (int i = 0; i < count; i++) sum += values[i];
    double mean = sum / count;
    double var = 0.0;
    for (int i = 0; i < count; i++) var += (values[i] - mean) * (values[i] - mean);
    double stddev = std::sqrt(var / count);
    // Check if last reading deviates beyond threshold
    if (std::fabs(values[count - 1] - mean) > threshold_sigma * stddev) return 1;
    return 0;
}

/**
 * 7. GUNAKASAMUCCAYA (Product Sum / Combined Factor)
 * Computes the holistic soil wellness score by combining all factors multiplicatively.
 * Returns a 0-100 wellness index.
 */
double gunakasamuccaya_wellness(
    double ph_score,
    double npk_score,
    double moisture_score,
    double organic_matter_score
) {
    // Geometric mean of all factors ensures any critical deficit drives score down
    double product = ph_score * npk_score * moisture_score * organic_matter_score;
    double geo_mean = std::pow(std::max(product, 0.0001), 0.25);
    return std::min(100.0, geo_mean);
}

/**
 * 8. SHUNYAM (Zero / Null Principle)
 * Identifies when complementary treatments cancel out stress.
 * Returns residual stress after applying organic amendment.
 * A result near 0 means perfect balance (Shunyam achieved).
 */
double shunyam_stress_balance(double stress_index, double amendment_potency) {
    double residual = stress_index - amendment_potency;
    if (std::fabs(residual) < 1.0) return 0.0; // Shunyam achieved
    return residual;
}

/**
 * AHIMSA-108 PROTOCOL
 * Computes the Ahimsa stress code. If returned value >= 108, soil is in critical stress.
 * Based on combined deficit, pH inversion severity, and anomaly flags.
 */
double ahimsa_108_stress_code(
    double nikhilam_deficit_val,
    double paravartya_deviation,
    int vilokanam_flag,
    double gunakasamuccaya_wellness_val
) {
    double base = (nikhilam_deficit_val / 40.0) * 60.0;
    double ph_penalty = std::fabs(paravartya_deviation) * 2.0;
    double anomaly_penalty = vilokanam_flag * 20.0;
    double wellness_penalty = (100.0 - gunakasamuccaya_wellness_val) * 0.3;
    return base + ph_penalty + anomaly_penalty + wellness_penalty;
}

} // extern "C"


extern "C" {
    // Ekadhikena: Predictive growth scaling (One more than the previous)
    // formula: current_height * (1 + growth_rate)
    float ekadhikena_growth(float current_height, float growth_rate) {
        return current_height * (1.0f + growth_rate);
    }

    // Gunakasamuccayah: Aggregated yield estimation
    // Simplified: Sum of product of factors (soil quality * water * seeds)
    float gunakasamuccayah_yield(float* factors, int n) {
        float total = 1.0f;
        for(int i = 0; i < n; i++) {
            total *= factors[i];
        }
        return total;
    }
}

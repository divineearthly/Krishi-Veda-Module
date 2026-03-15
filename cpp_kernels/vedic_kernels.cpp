
#include <iostream>
#include <vector>
#include <numeric>

extern "C" {
    // Anurupyena: Proportional scaling for irrigation
    // formula: (current_moisture / target_moisture) * base_flow
    float anurupyena_irrigation(float current, float target, float base_flow) {
        if (target <= 0) return 0.0f;
        float ratio = current / target;
        return (1.0f - ratio) * base_flow;
    }

    // Paravartya: Adaptive inversion for nutrient balancing
    // Used to calculate deficit: Target - Current
    void paravartya_nutrients(float* current, float* target, float* result, int n) {
        for(int i = 0; i < n; i++) {
            result[i] = target[i] - current[i];
        }
    }

    // Nikhilam: Deficit optimization (Subraction from Base 10/100)
    // Used for fertilizer reduction efficiency
    float nikhilam_efficiency(float value, float base) {
        return base - value;
    }
}

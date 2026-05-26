#include <iostream>
#include <string>
#include <cstdlib>

// Functional Ayurvedic Soil Profiling
// Maps physical telemetry to traditional Dosha imbalances
std::string calculate_soil_dosha(float temp, float moisture, float ph) {
    if (moisture < 35.0 && temp > 30.0) {
        return "VATA-PITTA IMBALANCE (High Heat, High Dryness). Requires cooling biomass and deep irrigation.";
    } else if (moisture > 65.0 && temp < 25.0) {
        return "KAPHA DOMINATION (Heavy, Cold, Waterlogged). Requires drainage and aeration.";
    } else if (ph < 5.8 && temp >= 28.0) {
        return "PITTA TOXICITY (Acidic, Hot). Requires alkaline buffering (lime/ash).";
    } else if (ph > 7.5 && moisture < 40.0) {
        return "VATA TOXICITY (Alkaline, Dry). Requires organic compost and sulfur.";
    }
    return "TRIDOSHIC BALANCE (Sama Prakriti). Optimal growth matrix.";
}

int main(int argc, char* argv[]) {
    // Expects arguments: ./veda_accelerator [temp] [moisture] [ph]
    if (argc < 4) {
        std::cerr << "[!] Error: Missing telemetry coordinates." << std::endl;
        return 1;
    }

    float temp = std::atof(argv[1]);
    float moisture = std::atof(argv[2]);
    float ph = std::atof(argv[3]);

    std::string dosha_profile = calculate_soil_dosha(temp, moisture, ph);
    
    // Output strictly the Dosha profile so Python can capture it
    std::cout << dosha_profile << std::endl;
    return 0;
}

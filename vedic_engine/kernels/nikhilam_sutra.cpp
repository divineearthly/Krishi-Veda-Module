
#include <iostream>
#include <cmath>

extern "C" {
    long long nikhilam_multiply(int a, int b) {
        // Find the nearest base (power of 10)
        int digits = (int)log10(std::max(a, b)) + 1;
        long long base = pow(10, digits);
        
        long long dev_a = a - base;
        long long dev_b = b - base;
        
        long long left_part = a + dev_b;
        long long right_part = dev_a * dev_b;
        
        return left_part * base + right_part;
    }
}

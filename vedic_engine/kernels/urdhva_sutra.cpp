
#include <iostream>
#include <vector>
#include <algorithm>

extern "C" {
    // Multi-digit multiplication using Urdhva Tiryagbhyam logic
    long long urdhva_multiply(int a, int b) {
        std::vector<int> digits_a, digits_b;
        int temp_a = a, temp_b = b;
        
        while(temp_a > 0) { digits_a.push_back(temp_a % 10); temp_a /= 10; }
        while(temp_b > 0) { digits_b.push_back(temp_b % 10); temp_b /= 10; }
        
        int n = digits_a.size();
        int m = digits_b.size();
        std::vector<int> res(n + m, 0);
        
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                res[i + j] += digits_a[i] * digits_b[j];
            }
        }
        
        long long final_res = 0;
        long long power = 1;
        int carry = 0;
        for (int i = 0; i < res.size(); i++) {
            int val = res[i] + carry;
            res[i] = val % 10;
            carry = val / 10;
            final_res += (long long)res[i] * power;
            power *= 10;
        }
        return final_res;
    }
}

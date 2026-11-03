#include <iostream>

double compute_ratio(double numerator, double denominator, bool valid) {
    double ratio; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-11-1]
    if (valid && denominator != 0.0) {
        ratio = numerator / denominator;
    } else {
        ratio = 0.0;
    }
    return ratio;
}

int main() {
    std::cout << compute_ratio(1.0, 2.0, true) << std::endl;
    return 0;
}

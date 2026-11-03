#include <iostream>

double compute_ratio(double numerator, double denominator, bool valid) {
    double ratio = (valid && denominator != 0.0) ? numerator / denominator : 0.0;
    return ratio;
}

int main() {
    std::cout << compute_ratio(1.0, 2.0, true) << std::endl;
    return 0;
}

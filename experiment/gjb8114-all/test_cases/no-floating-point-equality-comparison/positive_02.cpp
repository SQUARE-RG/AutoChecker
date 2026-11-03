#include <cmath>
#include <iostream>

bool differs_by_more_than_tolerance(double lhs, double rhs) {
    const double epsilon = 1e-6;
    return std::fabs(lhs - rhs) > epsilon;
}

int main() {
    double measurement = 3.14159;
    double expected = 3.141592;
    if (differs_by_more_than_tolerance(measurement, expected)) {
        std::cout << "outside tolerance\n";
    } else {
        std::cout << "within tolerance\n";
    }
    return 0;
}

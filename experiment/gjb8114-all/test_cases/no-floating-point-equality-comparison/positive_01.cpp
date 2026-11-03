#include <cmath>
#include <iostream>

bool equals_with_tolerance(double lhs, double rhs) {
    const double epsilon = 1e-9;
    return std::fabs(lhs - rhs) < epsilon;
}

int main() {
    double value = 0.1 + 0.2;
    if (equals_with_tolerance(value, 0.3)) {
        std::cout << "approximately equal\n";
    } else {
        std::cout << "different\n";
    }
    return 0;
}

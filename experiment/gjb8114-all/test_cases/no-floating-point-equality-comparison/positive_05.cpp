#include <cmath>
#include <iostream>

int main() {
    double a = 0.1 + 0.2;
    double b = 0.3;
    const double eps = 1e-9;
    if (std::abs(a - b) >= eps) {
        std::cout << "different\n";
    } else {
        std::cout << "almost equal\n";
    }
    return 0;
}

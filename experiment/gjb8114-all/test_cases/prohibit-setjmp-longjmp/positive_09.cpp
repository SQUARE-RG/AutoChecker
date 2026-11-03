#include <cmath>
#include <utility>

std::pair<bool, double> safe_divide(double a, double b) {
    if (std::fabs(b) < 1e-10) {
        return {false, 0.0};
    }
    return {true, a / b};
}

int main() {
    auto result = safe_divide(1.0, 0.0);
    if (!result.first) {
        return -1;
    }
    return 0;
}

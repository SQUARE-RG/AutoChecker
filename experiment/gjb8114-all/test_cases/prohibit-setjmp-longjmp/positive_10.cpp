#include <cmath>
#include <tuple>

std::tuple<bool, double> safe_divide(double a, double b) {
    if (std::fabs(b) < 1e-10) {
        return {false, 0.0};
    }
    return {true, a / b};
}

int main() {
    auto result = safe_divide(1.0, 0.0);
    bool ok = std::get<0>(result);
    double value = std::get<1>(result);
    if (!ok) {
        return -1;
    }
    (void)value;
    return 0;
}

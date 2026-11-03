#include <cmath>
#include <iostream>
#include <system_error>

std::error_code safe_divide(double numerator, double denominator, double& result) {
    if (std::fabs(denominator) < 1e-12) {
        return std::make_error_code(std::errc::invalid_argument);
    }
    result = numerator / denominator;
    return std::error_code{};
}

int main() {
    double value = 0.0;
    std::error_code ec = safe_divide(1.0, 0.0, value);
    if (ec) {
        std::cout << "error: " << ec.message() << '\n';
        return 1;
    }
    std::cout << value << '\n';
    return 0;
}

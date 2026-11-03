#include <cmath>
#include <iostream>

int main() {
    double value = 3.7;
    int result = static_cast<int>(std::round(value));
    std::cout << result << '\n';
    return 0;
}

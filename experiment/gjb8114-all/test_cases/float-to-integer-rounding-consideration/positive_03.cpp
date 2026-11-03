#include <cmath>
#include <iostream>

int round_to_int(double value) {
    return static_cast<int>(std::nearbyint(value));
}

int main() {
    double value = 7.8;
    int rounded = round_to_int(value);
    std::cout << rounded << std::endl;
    return 0;
}

#include <iostream>

double scale(double value) {
    return value * 2.0;
}

int main() {
    double input = 0.125;
    double output = scale(input);
    std::cout << output << '\n';
    return 0;
}

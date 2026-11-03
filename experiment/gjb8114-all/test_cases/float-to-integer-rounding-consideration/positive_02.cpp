#include <cmath>
#include <iostream>

int main() {
    double seconds = 125.0;
    long minutes = std::lround(seconds / 60.0);
    std::cout << minutes << '\n';
    return 0;
}

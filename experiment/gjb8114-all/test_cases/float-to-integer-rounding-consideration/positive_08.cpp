#include <cmath>
#include <iostream>

int main() {
    double measurement = 9.6;
    long rounded = std::lrint(measurement);
    std::cout << rounded << std::endl;
    return 0;
}

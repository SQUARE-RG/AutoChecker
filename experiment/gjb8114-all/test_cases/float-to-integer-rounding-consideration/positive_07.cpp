#include <cmath>
#include <iostream>

int main() {
    double raw = 8.7;
    int value = static_cast<int>(std::floor(raw));
    std::cout << value << std::endl;
    return 0;
}

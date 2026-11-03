#include <iostream>
#include <limits>

int main() {
    float f = std::numeric_limits<float>::max();
    double d = static_cast<double>(f);
    std::cout << d << std::endl;
    return 0;
}

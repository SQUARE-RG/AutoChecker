#include <cmath>
#include <iostream>

int main() {
    float value = 9.4f;
    int rounded = static_cast<int>(std::roundf(value));
    std::cout << rounded << std::endl;
    return 0;
}

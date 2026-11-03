#include <iostream>

int main() {
    int signedValue = -1;
    unsigned int unsignedValue = 1u;
    bool equal = (static_cast<long long>(signedValue) == static_cast<long long>(unsignedValue));
    std::cout << equal << std::endl;
    return 0;
}

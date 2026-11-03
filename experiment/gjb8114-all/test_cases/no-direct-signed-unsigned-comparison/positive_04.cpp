#include <iostream>

int main() {
    int signedValue = -1;
    unsigned int unsignedValue = 0u;
    int result = (signedValue > static_cast<long>(unsignedValue)) ? -1 : 1;
    std::cout << result << std::endl;
    return 0;
}

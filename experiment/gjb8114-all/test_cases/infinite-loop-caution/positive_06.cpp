#include <iostream>

int main() {
    unsigned int mask = 0x80U;
    while (mask != 0U) {
        std::cout << mask << std::endl;
        mask >>= 1U;
    }
    return 0;
}

#include <iostream>

int main() {
    unsigned long flags = 0x0F0FUL;
    unsigned long mask = 0x00FFUL;
    unsigned long combined = flags | mask;
    std::cout << combined << '\n';
    return 0;
}

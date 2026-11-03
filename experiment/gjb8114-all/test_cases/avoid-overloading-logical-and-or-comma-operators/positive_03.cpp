#include <iostream>

struct Bits {
    unsigned mask;

    Bits operator|(const Bits& other) const {
        return Bits{mask | other.mask};
    }
};

int main() {
    Bits a{0x1u};
    Bits b{0x2u};
    Bits c = a | b;
    return c.mask == 0x3u ? 0 : 1;
}

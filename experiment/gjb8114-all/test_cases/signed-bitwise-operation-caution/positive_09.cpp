#include <cstdint>
#include <iostream>

int main() {
    std::uint32_t flags = 1u;
    flags <<= 4;
    std::cout << flags << std::endl;
    return 0;
}

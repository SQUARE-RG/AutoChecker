#include <cstdint>
#include <iostream>

int main() {
    std::uint64_t value = 1ULL;
    std::uint64_t shifted = value << 3;
    std::cout << shifted << '\n';
    return 0;
}

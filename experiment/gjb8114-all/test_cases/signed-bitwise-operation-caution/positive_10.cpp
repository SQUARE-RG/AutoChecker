#include <cstdint>
#include <iostream>

int main() {
    std::uint64_t flags = 0x0F0F0F0F0F0F0F0FULL;
    std::uint64_t mask = 0x00FF00FF00FF00FFULL;
    std::uint64_t result = flags ^ mask;
    std::cout << result << std::endl;
    return 0;
}

#include <cstdint>

int main() {
    std::uint64_t value = 1024;
    std::uint64_t shift = 2;
    std::uint64_t result = value >> shift;
    return result == 256 ? 0 : 1;
}

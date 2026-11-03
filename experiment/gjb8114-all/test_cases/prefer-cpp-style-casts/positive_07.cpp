#include <cstdint>

int main() {
    std::uintptr_t raw = 0x1000;
    int* p = reinterpret_cast<int*>(raw);
    return p == nullptr ? 1 : 0;
}

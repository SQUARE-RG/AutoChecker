#include <cstdint>

int main() {
    int value = 7;
    int* ptr = &value;
    const int* qualified = ptr;
    std::int64_t plain = value;
    return *qualified + static_cast<int>(plain);
}

#include <cstdint>

int main() {
    int value = 5;
    int* ptr = &value;
    void* erased = ptr;
    int* restored = static_cast<int*>(erased);
    std::int64_t number = static_cast<std::int64_t>(value);
    return *restored + static_cast<int>(number);
}

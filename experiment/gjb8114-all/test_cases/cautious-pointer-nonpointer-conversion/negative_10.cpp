#include <cstdint>

struct PointerHolder {
    int* ptr;

    explicit PointerHolder(std::uintptr_t raw)
        : ptr(reinterpret_cast<int*>(raw)) {} // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-4]
};

int main() {
    PointerHolder holder{static_cast<std::uintptr_t>(0x1000u)};
    return holder.ptr == nullptr ? 0 : 1;
}

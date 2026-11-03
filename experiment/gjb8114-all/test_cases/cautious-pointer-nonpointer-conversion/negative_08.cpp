#include <cstdint>

int main() {
    int value = 7;
    int* p = &value;
    std::uintptr_t raw = std::uintptr_t(p); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-4]
    return static_cast<int>(raw != 0);
}

#include <cstdint>

int main() {
    std::uintptr_t raw = 0x1000;
    int* p = (int*)raw; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-5-1]
    return p == nullptr ? 1 : 0;
}

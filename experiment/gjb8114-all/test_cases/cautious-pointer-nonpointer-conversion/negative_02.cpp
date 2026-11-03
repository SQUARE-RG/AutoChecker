#include <cstdint>

int main() {
    std::uintptr_t raw = 0;
    int* ptr = reinterpret_cast<int*>(raw); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-4]
    return ptr == nullptr ? 0 : 1;
}

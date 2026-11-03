#include <cstdint>

int main() {
    std::intptr_t raw = 0x1000;
    int* ptr = (int*)raw;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-4]
    return ptr == nullptr;
}

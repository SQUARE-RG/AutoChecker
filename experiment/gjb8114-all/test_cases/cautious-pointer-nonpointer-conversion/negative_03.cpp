#include <cstdint>

int main() {
    int value = 42;
    int* ptr = &value;
    std::intptr_t address = reinterpret_cast<std::intptr_t>(ptr);  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-4]
    return 0;
}

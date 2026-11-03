#include <cstdint>

std::uint32_t* get_local_address() {
    std::uint32_t value = 42;
    return &value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-4]
}

int main() {
    std::uint32_t* p = get_local_address();
    (void)p;
    return 0;
}

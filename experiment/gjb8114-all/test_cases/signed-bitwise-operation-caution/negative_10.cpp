#include <cstdint>
#include <iostream>

int main() {
    std::int64_t flags = 0x0F;
    std::int64_t inverted = ~flags; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-1]
    std::cout << inverted << std::endl;
    return 0;
}

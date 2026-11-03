#include <cstdint>

int main() {
    int flags = 0x0F;
    int masked = flags & 0x03; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-1]
    (void)masked;
    return 0;
}

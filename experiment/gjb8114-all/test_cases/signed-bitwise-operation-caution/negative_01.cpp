#include <cstdint>

int main() {
    int value = 1;
    int shifted = value << 4; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-1]
    (void)shifted;
    return 0;
}

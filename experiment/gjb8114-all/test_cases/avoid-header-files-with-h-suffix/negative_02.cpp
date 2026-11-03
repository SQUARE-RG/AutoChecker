#include <stdlib.h> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-4]

int main() {
    int value = -7;
    int magnitude = abs(value);
    return magnitude == 7 ? 0 : 1;
}

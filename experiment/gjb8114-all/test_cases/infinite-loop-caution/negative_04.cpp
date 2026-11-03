#include <cstddef>

int main() {
    int index = 0;
    int total = 0;
    while (1) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-1]
        total += index;
        ++index;
        if (index >= 10) {
            break;
        }
    }
    return total == 45 ? 0 : 1;
}

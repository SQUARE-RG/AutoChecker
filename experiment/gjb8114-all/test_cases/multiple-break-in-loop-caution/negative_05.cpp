#include <iostream>

int main() {
    int limit = 10;
    int value = 0;
    for (;;) {
        ++value;
        if (value >= limit) {
            break;
        }
        if (value % 3 == 0) {
            std::cout << value << '\n';
            break; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-2]
        }
    }
    return 0;
}

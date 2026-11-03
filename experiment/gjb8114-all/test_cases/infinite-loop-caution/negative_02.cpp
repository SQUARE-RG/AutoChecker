#include <iostream>

int main() {
    int total = 0;
    for (;;) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-1]
        total += 2;
        std::cout << total << std::endl;
        if (total >= 10) {
            break;
        }
    }
    return 0;
}

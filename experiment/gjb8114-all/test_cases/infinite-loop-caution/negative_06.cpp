#include <iostream>

int main() {
    unsigned int value = 1;
    unsigned long total = 0;
    while (1 == 1) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-1]
        total += value;
        ++value;
        if (value > 100U) {
            value = 1U;
        }
    }
    std::cout << total << std::endl;
    return 0;
}

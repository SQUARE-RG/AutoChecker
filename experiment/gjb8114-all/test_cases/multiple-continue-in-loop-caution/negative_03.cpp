#include <iostream>

int main() {
    int total = 0;
    for (int i = 0; i < 10; ++i) {
        if (i % 2 == 0) {
            continue;
        }
        if (i > 7) {
            continue; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-3]
        }
        total += i;
    }
    std::cout << total << std::endl;
    return 0;
}

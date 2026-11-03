#include <iostream>

int main() {
    int i = 0;
    int sum = 0;
    do {
        ++i;
        if (i % 2 == 0) {
            continue;
        }
        if (i > 6) {
            continue; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-3]
        }
        sum += i;
    } while (i < 10);
    std::cout << sum << std::endl;
    return 0;
}

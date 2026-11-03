#include <iostream>

int main() {
    int count = 0;
    while (count < 2) {
        register int step = 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-13-2]
        count += step;
    }
    std::cout << count << std::endl;
    return 0;
}

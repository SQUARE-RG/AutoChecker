#include <iostream>

int main() {
    int total = 0;
    for (int i = 0; i < 5; ++i) {
        total += i;
    }  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-2-3]
    std::cout << total << std::endl;
    return 0;
}

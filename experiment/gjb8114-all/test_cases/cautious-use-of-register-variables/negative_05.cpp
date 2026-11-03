#include <iostream>

int main() {
    int sum = 0;
    if (sum == 0) {
        register const int offset = 3; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-13-2]
        sum += offset;
    }
    std::cout << sum << std::endl;
    return 0;
}

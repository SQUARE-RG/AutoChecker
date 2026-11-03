#include <iostream>

int main() {
    signed char value = 0x5A;
    int flipped = ~value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-1]
    std::cout << flipped << '\n';
    return 0;
}

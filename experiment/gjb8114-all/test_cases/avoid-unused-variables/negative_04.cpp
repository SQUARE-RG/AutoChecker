#include <iostream>

int main() {
    int used = 3, unused = 4; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-2]
    std::cout << used << '\n';
    return 0;
}

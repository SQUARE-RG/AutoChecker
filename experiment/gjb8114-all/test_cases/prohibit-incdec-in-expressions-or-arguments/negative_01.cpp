#include <iostream>

int main() {
    int x = 1;
    int y = x++ + 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-5]
    std::cout << y << std::endl;
    return 0;
}

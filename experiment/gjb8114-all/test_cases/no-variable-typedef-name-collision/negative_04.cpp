#include <iostream>

typedef int Triple[3];

int main() {
    Triple Triple = {1, 2, 3}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-6]
    std::cout << Triple[0] + Triple[1] + Triple[2] << std::endl;
    return 0;
}

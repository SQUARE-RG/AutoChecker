int g = (g = 1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-3]
#include <iostream>

int main() {
    std::cout << g << std::endl;
    return 0;
}

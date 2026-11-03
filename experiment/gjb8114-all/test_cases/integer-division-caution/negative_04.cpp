#include <iostream>

int quotient(int a, int b) {
    return a / b; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-2]
}

int main() {
    std::cout << quotient(17, 5) << std::endl;
    return 0;
}

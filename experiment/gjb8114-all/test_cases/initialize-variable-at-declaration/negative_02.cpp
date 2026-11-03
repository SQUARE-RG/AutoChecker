#include <iostream>

int main() {
    long number = 100;
    long* address; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-11-1]
    address = &number;
    std::cout << *address << std::endl;
    return 0;
}

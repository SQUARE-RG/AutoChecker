#include <iostream>

int main() {
    double measurement = 7.9;
    int value(measurement); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-1]
    std::cout << value << std::endl;
    return 0;
}

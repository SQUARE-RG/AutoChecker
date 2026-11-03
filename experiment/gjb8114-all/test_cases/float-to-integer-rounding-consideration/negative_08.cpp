#include <iostream>

int main() {
    double reading = 14.75;
    long whole = long(reading); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-1]
    std::cout << whole << std::endl;
    return 0;
}

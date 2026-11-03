#include <iostream>

double circle_area(double radius) {
    return 3.14159 * radius * radius; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-6]
}

int main() {
    const double radius = 2.0;
    std::cout << circle_area(radius) << std::endl;
    return 0;
}

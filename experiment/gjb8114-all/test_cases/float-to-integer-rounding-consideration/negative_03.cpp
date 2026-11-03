#include <iostream>

double scale(double value) {
    return value * 3.5;
}

int main() {
    double value = 7.8;
    int truncated = 0;
    truncated = (int)scale(value); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-1]
    std::cout << truncated << std::endl;
    return 0;
}

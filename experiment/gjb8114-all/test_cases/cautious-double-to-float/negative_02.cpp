#include <iostream>

void takeFloat(float x) {
    std::cout << x << std::endl;
}

int main() {
    double d = 2.718281828459045;
    takeFloat(d); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-2]
    return 0;
}

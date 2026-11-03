#include <iostream>

int main() {
    int values[10] = {};
    int index = 7;
    int divisor = 2;
    values[index / divisor] = 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-2]
    std::cout << values[3] << '\n';
    return 0;
}

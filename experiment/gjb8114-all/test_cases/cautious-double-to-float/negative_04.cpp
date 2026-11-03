#include <iostream>

float compute() {
    double value = 2.718281828459045;
    return value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-2]
}

int main() {
    float result = compute();
    std::cout << result << '\n';
    return 0;
}

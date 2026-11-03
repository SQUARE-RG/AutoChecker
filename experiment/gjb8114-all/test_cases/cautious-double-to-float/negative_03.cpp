#include <iostream>

int main() {
    double pi = 3.141592653589793;
    float result = static_cast<float>(pi); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-2]
    std::cout << result << '\n';
    return 0;
}

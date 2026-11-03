#include <iostream>

int main() {
    int a = 0;
    int b = 0;
    bool condition = true;
    int result = condition ? (a = 1, b = 2) : (b = 3); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-6]
    std::cout << result << std::endl;
    return 0;
}

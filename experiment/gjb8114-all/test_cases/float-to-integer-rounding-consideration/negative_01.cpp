#include <iostream>

int main() {
    float value = 3.75f;
    int result = value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-1]
    std::cout << result << '\n';
    return 0;
}

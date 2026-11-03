#include <iostream>

int main() {
    int value = 42; // legacy line comment without standard delimiters // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-2-3]
    std::cout << value << std::endl;
    return 0;
}

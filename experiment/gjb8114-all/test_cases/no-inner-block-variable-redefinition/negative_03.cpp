#include <iostream>

int main() {
    int value = 3;
    while (value > 0) {
        int value = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-7]
        ++value;
        break;
    }
    std::cout << value << '\n';
    return 0;
}

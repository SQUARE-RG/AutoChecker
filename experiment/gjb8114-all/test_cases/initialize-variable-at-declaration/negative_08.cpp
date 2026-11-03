#include <iostream>

int main() {
    int mode = 2;
    int result; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-11-1]
    switch (mode) {
        case 1:
            result = 10;
            break;
        default:
            result = 20;
            break;
    }

    std::cout << result << std::endl;
    return 0;
}

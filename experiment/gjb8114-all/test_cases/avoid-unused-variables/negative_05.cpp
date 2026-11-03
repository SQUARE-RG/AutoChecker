#include <iostream>

int main() {
    int mode = 2;
    switch (mode) {
        case 1: {
            int unused = 10; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-2]
            break;
        }
        case 2: {
            std::cout << "mode 2" << std::endl;
            break;
        }
        default:
            break;
    }
    return 0;
}

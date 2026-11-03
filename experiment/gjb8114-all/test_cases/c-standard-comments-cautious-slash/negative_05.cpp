#include <iostream>

int classify(int value) {
    switch (value) {
        case 0: // zero case
        // CHECK-MESSAGES: :[[@LINE-1]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-2-3]
            return 0;
        case 1:
            return 1;
        default:
            return -1;
    }
}

int main() {
    std::cout << classify(1) << '\n';
    return 0;
}

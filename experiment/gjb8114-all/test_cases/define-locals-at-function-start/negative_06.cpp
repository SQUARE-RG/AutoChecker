#include <iostream>

int compute(int value) {
    try {
        std::cout << "start\n";
    } catch (...) {
        std::cout << "error\n";
    }
    int adjusted = value * 4; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-4]
    return adjusted;
}

int main() {
    std::cout << compute(3) << '\n';
    return 0;
}

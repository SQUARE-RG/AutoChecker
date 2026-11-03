#include <iostream>

int classify(int value) {
    int result = 0;
    if (int doubled = value * 2; doubled > 18) { result = 1; } else if (int tripled = value * 3; tripled > 30) { result = 2; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-1]
    return result;
}

int main() {
    std::cout << classify(7) << '\n';
    return 0;
}

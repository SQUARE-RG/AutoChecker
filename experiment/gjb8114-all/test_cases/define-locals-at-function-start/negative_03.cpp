#include <iostream>

int compute(int value) {
    int total = 0;
    int i = 0;
    while (i < value) {
        total += i;
        int doubled = i * 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-4]
        total += doubled;
        ++i;
    }
    return total;
}

int main() {
    std::cout << compute(5) << '\n';
    return 0;
}

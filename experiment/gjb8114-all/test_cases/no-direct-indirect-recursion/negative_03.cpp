#include <iostream>

class Fibonacci {
public:
    int compute(int n) {
        if (n < 2) {
            return n;
        }
        return compute(n - 1) + compute(n - 2); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-16]
    }
};

int main() {
    Fibonacci fibonacci;
    std::cout << fibonacci.compute(6) << '\n';
    return 0;
}

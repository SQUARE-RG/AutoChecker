#include <iostream>

struct Accumulator {
    char current;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-20]
};

int main() {
    Accumulator acc;
    acc.current = 10;
    int next = acc.current + 5;
    std::cout << next << '\n';
    return 0;
}

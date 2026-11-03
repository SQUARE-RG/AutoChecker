#include <iostream>

int add(int a, int b) { return a + b; }

int main() {
    auto operation = &add; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-1]
    std::cout << operation(2, 3) << '\n';
    return 0;
}

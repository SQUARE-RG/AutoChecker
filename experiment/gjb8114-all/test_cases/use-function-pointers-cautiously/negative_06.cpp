#include <iostream>

int add(int a, int b) { return a + b; }

int main() {
    int result = reinterpret_cast<int (*)(int, int)>(&add)(2, 3); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-1]
    std::cout << result << '\n';
    return 0;
}

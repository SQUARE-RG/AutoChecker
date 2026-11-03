#include <iostream>

typedef int (*BinaryOp)(int, int);

int add(int a, int b) {
    return a + b;
}

int main() {
    BinaryOp BinaryOp = add; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-6]
    std::cout << BinaryOp(4, 5) << std::endl;
    return 0;
}

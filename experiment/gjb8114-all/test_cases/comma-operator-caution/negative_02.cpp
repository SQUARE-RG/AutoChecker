#include <iostream>

int combine(int a, int b) {
    return (a += 1, a + b); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-6]
}

int main() {
    int x = 1, y = 2;
    std::cout << combine(x, y);
    return 0;
}

#include <iostream>

void check(int x) {
    if (x > 0) {
        int a = 0;
        int b = 0;
        throw (a = x, b = a + 1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-6]
    }
}

int main() {
    try {
        check(2);
    } catch (int value) {
        std::cout << value << std::endl;
    }
    return 0;
}

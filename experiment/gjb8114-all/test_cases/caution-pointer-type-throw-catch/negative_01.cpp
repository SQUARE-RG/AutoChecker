#include <iostream>

int main() {
    int i = 0;
    try {
        int a1 = 1;
        int* a2 = new int(2);
        if (i > 10) {
            throw &a1;
        } else {
            throw a2;
        }
    } catch (int* b) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-8-2]
        std::cout << b << std::endl;
    }
    return 0;
}

#include <iostream>

void freeFunction() {}

int main() {
    try {
        void (*fp)() = &freeFunction;
        throw fp;
    } catch (void (*handler)()) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-8-2]
        (void)handler;
        std::cout << 1;
    }
    return 0;
}

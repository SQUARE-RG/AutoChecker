#include <iostream>
using IntPtr = int*;

int main() {
    int value = 42;
    try {
        IntPtr ptr = &value;
        throw ptr;
    } catch (IntPtr caught) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-8-2]
        std::cout << *caught;
    }
    return 0;
}

// Negative case 1: an object address is stored in an untyped void pointer.
#include <iostream>

int main() {
    int value = 42;
    void* untyped = &value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-2]
    int* typed = static_cast<int*>(untyped);
    std::cout << *typed << '\n';
    return 0;
}

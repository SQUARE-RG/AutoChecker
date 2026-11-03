#include <iostream>

int main() {
    int value = 42;
    void** handle = reinterpret_cast<void**>(&value); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-2]
    int* typed = reinterpret_cast<int*>(handle);
    std::cout << *typed << '\n';
    return 0;
}

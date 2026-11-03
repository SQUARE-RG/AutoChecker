#include <atomic>
#include <iostream>

int main() {
    int value = 42;
    std::atomic<void*> slot{&value}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-2]
    int* typed = static_cast<int*>(slot.load());
    std::cout << *typed << '\n';
    return 0;
}

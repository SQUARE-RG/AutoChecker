#include <iostream>

int main() {
    volatile int value = 5;
    int& ref = const_cast<int&>(value); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-5-2]
    (void)ref;
    return 0;
}

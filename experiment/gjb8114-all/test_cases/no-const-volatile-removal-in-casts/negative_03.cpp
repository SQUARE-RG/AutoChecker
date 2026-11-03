#include <iostream>

int main() {
    volatile int value = 10;
    volatile int* vp = &value;
    int* p = const_cast<int*>(vp); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-5-2]
    *p = 20;
    std::cout << *p << '\n';
    return 0;
}

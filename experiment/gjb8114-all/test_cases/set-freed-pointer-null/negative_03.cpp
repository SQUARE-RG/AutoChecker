#include <iostream>

int main() {
    int* p = new int(42);
    *p = *p + 1;
    delete p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-6]
    return 0;
}

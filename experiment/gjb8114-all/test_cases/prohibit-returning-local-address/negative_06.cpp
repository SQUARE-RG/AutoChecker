#include <iostream>

int* alias() {
    int local = 5;
    int* ptr = &local;
    return ptr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-4]
}

int main() {
    int* p = alias();
    (void)p;
    return 0;
}

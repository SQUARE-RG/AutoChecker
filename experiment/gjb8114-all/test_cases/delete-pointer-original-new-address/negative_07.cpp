#include <iostream>

int fun(void) {
    int *p = new int[3] + 1;
    if (p == nullptr) {
        return -1;
    }
    p[-1] = 1;
    p[0] = 2;
    p[1] = 3;
    delete[] p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-3]
    p = nullptr;
    return 0;
}

int main(void) {
    return fun();
}

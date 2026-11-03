#include <iostream>

int main() {
    int *p = new int[3];
    p[0] = 1;
    p++;
    p[0] = 2;
    delete[] p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-3]
    return 0;
}

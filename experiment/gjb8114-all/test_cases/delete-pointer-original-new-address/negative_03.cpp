#include <iostream>

int main() {
    int* p = new int[4];
    p[0] = 1;
    delete[] (p + 1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-3]
    return 0;
}

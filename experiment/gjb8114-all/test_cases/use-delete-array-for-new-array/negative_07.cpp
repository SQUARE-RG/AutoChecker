#include <iostream>

int main() {
    int *p = new int[5]();
    p[0] = 7;
    delete p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-2]
    return 0;
}

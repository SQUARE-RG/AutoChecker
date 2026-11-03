#include <iostream>

int main() {
    int *p = new int(7);
    *p = 3;
    p = p + 1;
    delete p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-3]
    return 0;
}

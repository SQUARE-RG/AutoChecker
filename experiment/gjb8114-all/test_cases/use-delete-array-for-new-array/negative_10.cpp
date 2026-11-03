#include <iostream>

int main() {
    int **p = new int*[5];
    p[0] = nullptr;
    p[1] = nullptr;
    delete p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-2]
    p = nullptr;
    return 0;
}

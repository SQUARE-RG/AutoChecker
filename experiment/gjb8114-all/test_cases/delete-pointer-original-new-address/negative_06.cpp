#include <iostream>

int main() {
    int* p = new int[4];
    int* q = new int[4];
    for (int i = 0; i < 4; ++i) {
        p[i] = i;
        q[i] = i;
    }
    p = q + 2;
    delete[] p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-3]
    return 0;
}

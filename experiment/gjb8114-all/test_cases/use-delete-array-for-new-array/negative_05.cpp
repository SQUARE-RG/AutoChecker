#include <iostream>

int main() {
    using IntArray = int[10];
    int* p = new IntArray;
    for (int i = 0; i < 10; ++i) {
        p[i] = i;
    }
    delete p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-2]
    return 0;
}

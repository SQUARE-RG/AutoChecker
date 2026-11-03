#include <iostream>

void advance(int*& ptr) {
    ++ptr;
}

int main() {
    int* p = new int[3];
    p[0] = 1;
    p[1] = 2;
    p[2] = 3;
    advance(p);
    delete[] p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-3]
    return 0;
}

#include <iostream>

struct Holder {
    int* ptr;
};

int main() {
    Holder h;
    h.ptr = new int[3];
    for (int i = 0; i < 3; ++i) {
        h.ptr[i] = i;
    }
    h.ptr += 1;
    delete[] h.ptr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-3]
    return 0;
}

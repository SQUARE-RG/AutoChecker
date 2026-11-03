#include <iostream>

int main() {
    auto* p = new short[8];
    p[0] = 1;
    p[1] = 2;
    p[2] = 3;
    delete p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-2]
    p = nullptr;
    return 0;
}

#include <iostream>

int main() {
    int* values = new int[3];
    values[0] = 1;
    values[1] = 2;
    values[2] = 3;
    delete values; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-2]
    values = nullptr;
    return 0;
}

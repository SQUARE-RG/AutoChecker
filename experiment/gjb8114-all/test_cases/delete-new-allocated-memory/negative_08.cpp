#include <iostream>
#include <new>

int main() {
    int* values = new (std::nothrow) int[4]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-1]
    if (values == nullptr) {
        return 1;
    }

    values[0] = 10;
    values[1] = 20;
    values[2] = 30;
    values[3] = 40;

    std::cout << values[0] + values[3] << std::endl;
    return 0;
}

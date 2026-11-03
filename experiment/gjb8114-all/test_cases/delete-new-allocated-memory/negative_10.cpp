#include <iostream>

int main() {
    int *p = new int[0]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-1]
    if (p != nullptr) {
        std::cout << "allocated" << std::endl;
    }
    return 0;
}

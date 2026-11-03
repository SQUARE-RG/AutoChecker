#include <iostream>

int main() {
    int* p = new int(7);
    try {
        throw p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-8-2]
    } catch (int* e) {
        std::cout << *e << std::endl;
        delete e;
    }
    return 0;
}

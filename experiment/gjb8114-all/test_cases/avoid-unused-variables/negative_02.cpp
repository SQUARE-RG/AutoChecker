#include <iostream>
int main() {
    for (int i = 0; i < 3; ++i) {
        int unused_in_loop = i * 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-2]
        std::cout << i << std::endl;
    }
    return 0;
}

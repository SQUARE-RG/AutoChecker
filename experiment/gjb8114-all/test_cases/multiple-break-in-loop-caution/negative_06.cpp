#include <iostream>

int main() {
    int threshold = 5;
    for (int i = 0; i < 10; ++i) {
        if (i >= threshold) {
            break;
        }
        std::cout << i << '\n';
        break; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-2]
    }
    return 0;
}

#include <cstdlib>
#include <iostream>

int main() {
    int* buffer = static_cast<int*>(std::calloc(8, sizeof(int)));  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-3]
    if (buffer == nullptr) {
        return 1;
    }
    buffer[0] = 7;
    std::cout << buffer[0];
    return 0;
}

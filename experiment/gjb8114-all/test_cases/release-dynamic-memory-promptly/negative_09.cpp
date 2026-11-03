#include <iostream>
#include <memory>

int main() {
    std::allocator<int> alloc;
    int* buffer = alloc.allocate(4); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-3]
    for (int i = 0; i < 4; ++i) {
        buffer[i] = i * 3;
    }
    int sum = 0;
    for (int i = 0; i < 4; ++i) {
        sum += buffer[i];
    }
    std::cout << sum << std::endl;
    return 0;
}

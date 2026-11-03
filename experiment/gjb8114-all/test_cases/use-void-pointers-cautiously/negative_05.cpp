#include <cstdlib>
#include <iostream>

int main() {
    void* raw = std::malloc(sizeof(int)); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-2]
    if (raw == nullptr) {
        return 1;
    }
    *static_cast<int*>(raw) = 7;
    std::cout << *static_cast<int*>(raw) << '\n';
    std::free(raw);
    return 0;
}

#include <iostream>

struct Holder {
    void* data;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-2]
};

int main() {
    int value = 42;
    Holder h;
    h.data = &value;
    int* restored = static_cast<int*>(h.data);
    std::cout << *restored << std::endl;
    return 0;
}

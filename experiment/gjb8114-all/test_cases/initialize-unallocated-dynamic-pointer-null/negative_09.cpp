#include <cstdlib>

int main() {
    auto allocate = []() {
        int* p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-7]
        p = static_cast<int*>(std::malloc(sizeof(int)));
        if (p != nullptr) {
            *p = 42;
        } else {
            return -1;
        }
        std::free(p);
        return 0;
    };
    return allocate();
}

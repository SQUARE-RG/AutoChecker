#include <cstdlib>

int main() {
    int* p = static_cast<int*>(std::malloc(sizeof(int)));
    if (p == nullptr) {
        return 1;
    }
    *p = 42;
    auto release = [&p]() {
        std::free(p); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-6]
    };
    release();
    return 0;
}

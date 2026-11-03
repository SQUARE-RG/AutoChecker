#include <cstdlib>

int main() {
    int* p, *q = nullptr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-7]
    p = static_cast<int*>(std::realloc(nullptr, sizeof(int)));
    if (p != nullptr) {
        *p = 42;
    }
    q = p;
    std::free(q);
    return 0;
}

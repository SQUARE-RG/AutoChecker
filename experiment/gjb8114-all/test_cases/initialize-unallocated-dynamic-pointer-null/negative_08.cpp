#include <cstdlib>

int main() {
    using IntPtr = int*;
    IntPtr p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-7]
    p = static_cast<IntPtr>(std::aligned_alloc(alignof(int), sizeof(int)));
    if (p != nullptr) {
        *p = 7;
    }
    std::free(p);
    return 0;
}

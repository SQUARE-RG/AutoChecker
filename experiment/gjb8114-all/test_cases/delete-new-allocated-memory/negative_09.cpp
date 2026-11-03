#include <new>

int main() {
    int *p = new (std::nothrow) int(42); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-1]
    if (p != nullptr) {
        *p += 1;
    }
    return 0;
}

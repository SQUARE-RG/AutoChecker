#include <new>

int main() {
    int *p = new (std::nothrow) int[6];
    if (p == nullptr) {
        return 1;
    }
    p[0] = 1;
    p[5] = 6;
    delete p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-2]
    return 0;
}

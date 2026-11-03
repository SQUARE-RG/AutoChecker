#include <cstddef>

int main() {
    int value = 7;
    int* p = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-9]
    p = &value;
    return *p;
}

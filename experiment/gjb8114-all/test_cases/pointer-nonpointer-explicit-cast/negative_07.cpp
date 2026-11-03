#include <cstddef>

static bool pointer_to_bool(int* p) {
    return p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-5]
}

int main() {
    int value = 0;
    int* ptr = &value;
    return pointer_to_bool(ptr) ? 0 : 1;
}

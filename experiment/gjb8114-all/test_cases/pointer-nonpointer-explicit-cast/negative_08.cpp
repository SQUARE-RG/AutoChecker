#include <cstddef>

static bool accept_bool(bool flag) {
    return flag;
}

int main() {
    int value = 0;
    int* ptr = &value;
    return accept_bool(ptr) ? 0 : 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-5]
}

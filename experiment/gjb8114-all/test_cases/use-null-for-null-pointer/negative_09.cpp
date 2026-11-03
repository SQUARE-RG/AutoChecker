#include <cstddef>

int main() {
    int value = 1;
    int* pointers[2] = { &value, 0 }; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-9]
    return pointers[0] == &value ? 0 : 1;
}

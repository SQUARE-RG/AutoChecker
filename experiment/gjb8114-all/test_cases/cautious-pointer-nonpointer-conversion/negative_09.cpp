#include <cstdlib>

int main() {
    int value = 5;
    int* ptr = &value;
    bool flag{ptr}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-4]
    return flag ? EXIT_SUCCESS : EXIT_FAILURE;
}

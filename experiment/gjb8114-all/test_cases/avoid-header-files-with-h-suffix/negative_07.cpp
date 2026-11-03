#include <assert.h> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-4]

int main() {
    int value = 1;
    assert(value == 1);
    return 0;
}

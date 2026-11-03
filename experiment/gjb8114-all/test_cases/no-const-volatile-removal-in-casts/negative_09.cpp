#include <cstddef>

int main() {
    const int value = 42;
    int* mutable_ptr = (int*)&value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-5-2]
    *mutable_ptr = 7;
    return 0;
}

#include <cstdint>

int main() {
    int value = 42;
    unsigned int* unsigned_ptr = (unsigned int*)&value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-5-1]
    *unsigned_ptr = 7u;
    return value;
}

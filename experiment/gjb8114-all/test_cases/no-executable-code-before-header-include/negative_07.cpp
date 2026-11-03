int* global_ptr = new int(42);

#include <ciso646> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-3]

int main() {
    return *global_ptr;
}

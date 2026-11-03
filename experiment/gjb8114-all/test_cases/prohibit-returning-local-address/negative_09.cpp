#include <memory>

int* returnAddressOfLocal() {
    int local = 7;
    return std::addressof(local); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-4]
}

#include <cstdlib>

int main() {
    int value = 42;
    int* p = &value;
    std::free(p); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-5]
    return 0;
}

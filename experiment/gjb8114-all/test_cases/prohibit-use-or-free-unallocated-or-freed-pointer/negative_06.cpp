#include <cstdlib>

int main() {
    int* p = new int(5);
    std::free(p); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-5]
    return 0;
}

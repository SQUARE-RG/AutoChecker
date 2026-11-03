#include <cstdlib>

int main() {
    int* p = static_cast<int*>(std::malloc(3 * sizeof(int)));
    if (p == nullptr) {
        return 1;
    }
    p[0] = 1;
    p[1] = 2;
    p += 1;
    std::free(p); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-17]
    return 0;
}

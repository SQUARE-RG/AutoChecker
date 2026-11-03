#include <cstdlib>

int main() {
    int *p = static_cast<int *>(std::malloc(sizeof(int)));
    if (p == nullptr) {
        return 0;
    }
    *p = 7;
    int *q = static_cast<int *>(std::realloc(p, 2 * sizeof(int)));
    if (q == nullptr) {
        std::free(p);
        return 0;
    }
    q[1] = 9;
    int value = *p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-5]
    std::free(q);
    return value;
}

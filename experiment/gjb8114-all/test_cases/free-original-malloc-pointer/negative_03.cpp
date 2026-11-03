#include <cstdlib>

int main() {
    int *p = static_cast<int*>(std::malloc(5 * sizeof(int)));
    if (p == nullptr) {
        return 1;
    }

    p[0] = 10;
    p[1] = 20;

    int *q = &p[1];
    q[0] = 30;

    std::free(q); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-17]
    return 0;
}

#include <cstdio>
#include <cstdlib>

int main() {
    long* values = static_cast<long*>(std::malloc(2 * sizeof(long)));
    std::scanf("%ld", values + 1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-8]
    return 0;
}

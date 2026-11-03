#include <cstdio>

int main() {
    int total = 0;
    for (int i = 0; i < 10; ++i) {
        if (i % 3 == 0) {
            goto skip_iteration;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-5-1]
        }
        total += i;
    skip_iteration:
        ;
    }
    std::printf("%d\n", total);
    return 0;
}
